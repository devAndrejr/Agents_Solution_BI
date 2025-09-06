import pandas as pd
import os

PARQUET_DIR = "data/parquet"


def inspect_parquet_file(filename):
    filepath = os.path.join(PARQUET_DIR, filename)
    if os.path.exists(filepath):
        try:
            df = pd.read_parquet(filepath)
            print(f"\n--- Colunas em {filename} ---")
            for col in df.columns:
                print(col)
        except Exception as e:
            print(f"Erro ao ler {filename}: {e}")
    else:
        print(f"Arquivo {filename} não encontrado.")


if __name__ == "__main__":
    inspect_parquet_file("ADMAT.parquet")
    inspect_parquet_file("ADMAT_SEMVENDAS.parquet")
    inspect_parquet_file("ADMMATAO.parquet")
