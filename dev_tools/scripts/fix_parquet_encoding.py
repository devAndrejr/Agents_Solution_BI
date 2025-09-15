import pandas as pd
import os

def fix_parquet_columns(file_path):
    """Corrige os nomes das colunas de um arquivo Parquet e o salva novamente."""
    try:
        df = pd.read_parquet(file_path)
        print(f"Colunas encontradas em {os.path.basename(file_path)}: {df.columns.tolist()}")
        
        columns_to_rename = {}
        for col in df.columns:
            if 'CDIGO' in col:
                columns_to_rename[col] = 'CODIGO'
            elif 'PREO 38%' in col:
                columns_to_rename[col] = 'PRECO_38PERCENT'

        if columns_to_rename:
            df.rename(columns=columns_to_rename, inplace=True)
            df.to_parquet(file_path, index=False)
            print(f"Colunas corrigidas em: {file_path}")
        else:
            print(f"Nenhuma coluna para corrigir em: {file_path}")

    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")

if __name__ == "__main__":
    parquet_dir = os.path.join(os.getcwd(), "data", "parquet")
    files_to_fix = ["ADMAT.parquet", "ADMAT_SEMVENDAS.parquet"]
    
    for file_name in files_to_fix:
        file_path = os.path.join(parquet_dir, file_name)
        if os.path.exists(file_path):
            fix_parquet_columns(file_path)
        else:
            print(f"Arquivo não encontrado: {file_path}")