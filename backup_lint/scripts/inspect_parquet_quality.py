
import pandas as pd
import glob
import os

def analyze_parquet_file(file_path):
    """
    Lê um arquivo Parquet, analisa sua estrutura, tipos de dados e qualidade.
    """
    print(f"--- Análise do Arquivo: {os.path.basename(file_path)} ---")
    
    try:
        df = pd.read_parquet(file_path)
        
        # 1. Informações Gerais
        print("\n[+] Informações Gerais:")
        print(f"  - Total de Linhas: {len(df)}")
        print(f"  - Total de Colunas: {len(df.columns)}")
        
        # 2. Schema e Tipos de Dados
        print("\n[+] Schema e Tipos de Dados:")
        print(df.info())
        
        # 3. Amostra dos Dados
        print("\n[+] Amostra dos Dados (Primeiras 5 Linhas):")
        print(df.head())
        
        # 4. Análise de Valores Nulos
        print("\n[+] Análise de Valores Nulos (Por Coluna):")
        null_counts = df.isnull().sum()
        null_percentages = (null_counts / len(df)) * 100
        null_df = pd.DataFrame({
            'Valores Nulos': null_counts,
            'Porcentagem (%)': null_percentages
        })
        print(null_df[null_df['Valores Nulos'] > 0].sort_values(by='Porcentagem (%)', ascending=False))
        
        # 5. Análise de Tipos Inconsistentes (Exemplo)
        print("\n[+] Verificação de Tipos de Dados Potencialmente Inconsistentes:")
        for col in df.select_dtypes(include=['object']).columns:
            try:
                # Tenta converter para numérico. Se a maioria for convertida, pode ser um tipo inconsistente.
                pd.to_numeric(df[col], errors='raise')
                print(f"  - AVISO: A coluna '{col}' é do tipo 'object', mas parece conter apenas dados numéricos.")
            except (ValueError, TypeError):
                # A coluna contém texto não numérico, o que é esperado para 'object'.
                pass

    except Exception as e:
        print(f"\n[!] Erro ao ler ou analisar o arquivo: {e}")
    
    print("\n"+"="*50+"\n")

def main():
    """
    Função principal para encontrar e analisar todos os arquivos Parquet.
    """
    parquet_files = glob.glob("data/parquet/**/*.parquet", recursive=True)
    
    if not parquet_files:
        print("Nenhum arquivo Parquet encontrado na pasta 'data/parquet/'.")
        return
        
    print(f"Encontrados {len(parquet_files)} arquivos Parquet. Iniciando análise...")
    
    for file in parquet_files:
        analyze_parquet_file(file)

if __name__ == "__main__":
    main()
