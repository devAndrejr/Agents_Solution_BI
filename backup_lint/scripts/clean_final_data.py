
import pandas as pd
import os

def clean_numeric_columns(file_path):
    """Lê um arquivo Parquet, força colunas potencialmente numéricas a serem numéricas (convertendo erros para NaN) e o salva novamente."""
    print(f"--- Limpando arquivo: {os.path.basename(file_path)} ---")
    try:
        df = pd.read_parquet(file_path)
        
        # Heurística para identificar colunas que deveriam ser numéricas
        potential_numeric_cols = [col for col in df.columns if df[col].dtype == 'object' and ('VENDA' in col.upper() or 'QTD' in col.upper() or 'PRECO' in col.upper() or 'VALOR' in col.upper() or 'MES' in col.upper() or '202' in col)]

        if not potential_numeric_cols:
            print("Nenhuma coluna de texto com aparência numérica para limpar.")
            # Mesmo que não encontre colunas de texto, vamos garantir que as colunas já numéricas estão corretas
            df.to_parquet(file_path, index=False)
            print("Arquivo re-salvo sem alterações de tipo.")
            return

        print(f"Colunas a serem convertidas para numérico: {potential_numeric_cols}")

        for col in potential_numeric_cols:
            original_non_numeric_count = pd.to_numeric(df[col], errors='coerce').isna().sum()
            df[col] = pd.to_numeric(df[col], errors='coerce')
            cleaned_non_numeric_count = df[col].isna().sum()
            if cleaned_non_numeric_count > original_non_numeric_count:
                 print(f"  - Coluna '{col}': Valores não numéricos convertidos para NaN.")

        # Salva o DataFrame limpo, substituindo o original
        df.to_parquet(file_path, index=False)
        print(f"\nArquivo {os.path.basename(file_path)} foi limpo e salvo com sucesso.")

    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")

if __name__ == "__main__":
    # Focar a limpeza apenas no arquivo de análise designado
    file_to_clean = "ADMAT_structured.parquet"
    parquet_dir = os.path.join(os.getcwd(), "data", "parquet_cleaned")
    file_path = os.path.join(parquet_dir, file_to_clean)

    if os.path.exists(file_path):
        clean_numeric_columns(file_path)
    else:
        print(f"ERRO: Arquivo de destino não encontrado: {file_path}")
