import pandas as pd
import os

parquet_dir = r'C:\Users\André\Documents\Agent_BI\data\parquet_cleaned'
file_name = "admmatao.parquet"

file_path = os.path.join(parquet_dir, file_name)

try:
    df = pd.read_parquet(file_path)
    print(f"Colunas em {file_name}: {df.columns.tolist()}")
except FileNotFoundError:
    print(f"Erro: Arquivo {file_name} não encontrado em {parquet_dir}")
except Exception as e:
    print(f"Ocorreu um erro ao ler o arquivo Parquet: {e}")
