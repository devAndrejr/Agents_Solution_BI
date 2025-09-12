import pandas as pd
import os

def inspect_column(file_path, column_name):
    """
    Carrega um arquivo Parquet e inspeciona os valores únicos de uma coluna.
    """
    try:
        df = pd.read_parquet(file_path)
        
        if column_name in df.columns:
            unique_values = df[column_name].unique()
            print(f"Valores únicos na coluna '{column_name}':")
            for value in unique_values:
                print(value)
        else:
            print(f"A coluna '{column_name}' não foi encontrada no arquivo.")
            
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    parquet_file = os.path.join(os.getcwd(), "data", "parquet_cleaned", "ADMAT_REBUILT.parquet")
    column_to_inspect = "nomesegmento"
    
    print(f"Inspecionando a coluna '{column_to_inspect}' no arquivo '{os.path.basename(parquet_file)}'...")
    inspect_column(parquet_file, column_to_inspect)
    print("Inspeção concluída.")
