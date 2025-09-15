import pandas as pd
import os

parquet_dir = r'C:\Users\André\Documents\Agent_BI\data\parquet_cleaned'
file_name = "admatao.parquet"

file_path = os.path.join(parquet_dir, file_name)

try:
    df = pd.read_parquet(file_path)
    print(f"Colunas em {file_name}: {df.columns.tolist()}")
    print(f"Shape de {file_name}: {df.shape}")

    # Verificar dados para o produto 369947
    produto_id = 369947 # Assumindo que PRODUTO é numérico
    if 'PRODUTO' in df.columns:
        df_produto = df[df['PRODUTO'] == produto_id]
        print(f"\nDados para o produto {produto_id}:\n")
        if not df_produto.empty:
            print(df_produto.head())
            print(f"Número de linhas para o produto {produto_id}: {len(df_produto)}")
        else:
            print(f"Nenhum dado encontrado para o produto {produto_id}.")
    else:
        print("Coluna 'PRODUTO' não encontrada no DataFrame.")

    # Verificar colunas de vendas
    colunas_vendas = ['MES_01', 'MES_02', 'MES_03', 'MES_04', 'MES_05', 'MES_06', 'MES_07', 'MES_08', 'MES_09', 'MES_10', 'MES_11', 'MES_12']
    print("\nVerificando colunas de vendas:")
    for col in colunas_vendas:
        if col in df.columns:
            print(f"Coluna '{col}' encontrada. Tipo: {df[col].dtype}")
        else:
            print(f"Coluna '{col}' NÃO encontrada.")

except FileNotFoundError:
    print(f"Erro: Arquivo {file_name} não encontrado em {parquet_dir}")
except Exception as e:
    print(f"Ocorreu um erro ao ler o arquivo Parquet ou processar os dados: {e}")
