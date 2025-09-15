
import pandas as pd
import os

def rename_all_columns(file_path):
    """Lê um arquivo Parquet, corrige sistematicamente os erros de codificação nos nomes das colunas e o salva novamente."""
    print(f"--- Corrigindo todos os nomes de colunas em: {os.path.basename(file_path)} ---")
    try:
        df = pd.read_parquet(file_path)
        original_columns = df.columns.tolist()
        
        # Mapeamento de correções conhecidas
        # A chave é o nome incorreto, o valor é o nome correto.
        # Adicionaremos mais mapeamentos conforme necessário.
        corrections_map = {
            'CDIGO': 'CODIGO',
            'PREO_38PERCENT': 'PRECO_38PERCENT',
            'SOLICITAO_DE_PREO': 'SOLICITACAO_DE_PRECO'
            # Adicione outros mapeamentos específicos aqui se souber deles
        }

        new_columns = []
        renamed_count = 0
        for col in original_columns:
            # Primeiro, tenta a correção genérica
            # Substitui o caractere de erro comum por letras prováveis
            # Esta é uma heurística e pode não ser perfeita, mas resolve o problema da chave.
            new_col_name = col.replace('', 'O') # Suposição comum
            new_col_name = new_col_name.replace('', 'A')
            new_col_name = new_col_name.replace('', 'C')
            new_col_name = new_col_name.replace('', 'E')
            new_col_name = new_col_name.replace('', 'I')
            new_col_name = new_col_name.replace('', 'U')

            # Aplica correções específicas conhecidas, que são mais confiáveis
            if col in corrections_map:
                new_col_name = corrections_map[col]
            
            if new_col_name != col:
                renamed_count += 1
            
            new_columns.append(new_col_name)

        if renamed_count > 0:
            df.columns = new_columns
            df.to_parquet(file_path, index=False)
            print(f"{renamed_count} colunas foram renomeadas com sucesso.")
            print(f"Arquivo {os.path.basename(file_path)} foi salvo com as colunas corrigidas.")
            # print(f"Novas colunas: {df.columns.tolist()}") # Descomente para depuração
        else:
            print("Nenhuma coluna precisou de renomeação com base nas regras atuais.")

    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")

if __name__ == "__main__":
    file_to_fix = "ADMAT_structured.parquet"
    parquet_dir = os.path.join(os.getcwd(), "data", "parquet_cleaned")
    file_path = os.path.join(parquet_dir, file_to_fix)

    if os.path.exists(file_path):
        rename_all_columns(file_path)
    else:
        print(f"ERRO: Arquivo de destino não encontrado: {file_path}")
