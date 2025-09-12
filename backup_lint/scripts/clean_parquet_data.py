import pandas as pd
import glob
import os
import unicodedata

def normalize_column_name(col_name):
    """
    Normaliza os nomes das colunas:
    - Remove acentos e caracteres especiais.
    - Substitui espaços e pontos por underscores.
    - Converte para maiúsculas.
    """
    # Remove acentos
    nfkd_form = unicodedata.normalize('NFKD', str(col_name))
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')
    # Substitui caracteres problemáticos e espaços
    no_special_chars = only_ascii.replace(' ', '_').replace('.', '').replace('%', 'PERCENT')
    return no_special_chars.upper()

def clean_parquet_file(file_path, output_dir):
    """
    Lê um arquivo Parquet, limpa os dados e salva em um novo local.
    """
    base_name = os.path.basename(file_path)
    print(f"--- Processando arquivo: {base_name} ---")

    try:
        df = pd.read_parquet(file_path)

        # 1. Normalizar nomes das colunas e garantir unicidade
        print("  - Normalizando nomes das colunas...")
        original_columns = df.columns
        new_columns = [normalize_column_name(col) for col in original_columns]
        
        # Lógica para garantir nomes únicos
        final_columns = []
        counts = {}
        for col in new_columns:
            if col in counts:
                counts[col] += 1
                final_columns.append(f"{col}_{counts[col]}")
            else:
                counts[col] = 0
                final_columns.append(col)
        
        df.columns = final_columns

        # 2. Corrigir tipos de dados específicos
        # Para ADMAT_SEMVENDAS.parquet, corrigir a coluna de data
        if "ADMAT_SEMVENDAS" in base_name and 'DATACRIALINHAVERDE' in df.columns:
            print("  - Corrigindo tipo da coluna 'DATACRIALINHAVERDE'...")
            df['DATACRIALINHAVERDE'] = pd.to_datetime(df['DATACRIALINHAVERDE'], errors='coerce')

        # 3. Otimizar memória (convertendo object para category onde fizer sentido)
        print("  - Otimizando tipos de dados (object -> category)...")
        object_cols = df.select_dtypes(include=['object']).columns
        print(f"    - Encontradas {len(object_cols)} colunas do tipo 'object' para otimizar.")
        for col in object_cols:
            try:
                # Heurística: se a cardinalidade for menor que 50%
                if df[col].nunique() / len(df) < 0.5:
                    df[col] = df[col].astype('category')
            except Exception as inner_e:
                print(f"      - AVISO: Nao foi possivel otimizar a coluna '{col}'. Erro: {inner_e}")
                continue

        # 4. Salvar o arquivo limpo
        output_path = os.path.join(output_dir, base_name)
        print(f"  - Salvando arquivo limpo em: {output_path}")
        df.to_parquet(output_path, index=False)

        print(f"  - Processamento concluído com sucesso.")

    except Exception as e:
        print(f"\n[!] Erro ao processar o arquivo {base_name}: {e}")

    print("\n" + "="*50 + "\n")

def main():
    """
    Função principal para limpar todos os arquivos Parquet.
    """
    input_dir = "data/parquet/"
    output_dir = "data/parquet_cleaned/"

    # Criar o diretório de saída se não existir
    if not os.path.exists(output_dir):
        print(f"Criando diretório de saída: {output_dir}")
        os.makedirs(output_dir)

    parquet_files = glob.glob(os.path.join(input_dir, "*.parquet"))

    if not parquet_files:
        print(f"Nenhum arquivo Parquet encontrado em '{input_dir}'.")
        return

    print(f"Encontrados {len(parquet_files)} arquivos Parquet. Iniciando limpeza...")

    for file in parquet_files:
        clean_parquet_file(file, output_dir)

    print("Limpeza de todos os arquivos concluída.")

if __name__ == "__main__":
    main()
