
import pandas as pd
import os
from collections import Counter

def diagnose_numeric_columns(file_path):
    """Analisa um arquivo Parquet e reporta valores não numéricos em colunas potencialmente numéricas."""
    print(f"\n--- Diagnosticando arquivo: {os.path.basename(file_path)} ---")
    try:
        df = pd.read_parquet(file_path)
        non_numeric_values = Counter()

        # Identifica colunas que deveriam ser numéricas (incluindo colunas de data/hora que podem ter texto)
        potential_numeric_cols = [col for col in df.columns if 'VENDA' in col.upper() or 'QTD' in col.upper() or 'PRECO' in col.upper() or 'VALOR' in col.upper() or 'MES' in col.upper() or '202' in col]

        if not potential_numeric_cols:
            print("Nenhuma coluna numérica potencial encontrada para análise.")
            return

        print(f"Colunas analisadas: {potential_numeric_cols}")

        for col in potential_numeric_cols:
            # Força a conversão para numérico, transformando não-numéricos em NaT/NaN
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            
            # Encontra os índices onde a conversão falhou (ou seja, onde estava o texto)
            non_numeric_mask = numeric_series.isna() & df[col].notna()
            
            if non_numeric_mask.any():
                # Pega os valores de texto originais usando a máscara
                text_values = df[col][non_numeric_mask]
                non_numeric_values.update(text_values.unique().tolist())

        if not non_numeric_values:
            print("Nenhum valor de texto encontrado nas colunas numéricas. O arquivo parece limpo.")
        else:
            print("\nRelatório de valores não numéricos encontrados:")
            for value, count in non_numeric_values.items():
                print(f"  - Valor: '{value}' (encontrado em {count} coluna(s) distinta(s)) ")

    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")

if __name__ == "__main__":
    parquet_dir = os.path.join(os.getcwd(), "data", "parquet_cleaned")
    
    files_to_scan = [f for f in os.listdir(parquet_dir) if f.endswith('.parquet')]

    if not files_to_scan:
        print(f"Nenhum arquivo .parquet encontrado em {parquet_dir}")
    else:
        for file_name in files_to_scan:
            file_path = os.path.join(parquet_dir, file_name)
            diagnose_numeric_columns(file_path)
