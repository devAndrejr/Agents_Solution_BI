import pandas as pd
import os

file_name = "ADMAT_REBUILT.parquet"
file_path = os.path.join('X:\\Meu Drive\\Caçula\\Langchain\\Agent_BI\\data\\parquet_cleaned', file_name)
df = pd.read_parquet(file_path)

# Filtrar o DataFrame pelo produto desejado
df_produto = df[df['CODIGO'] == 369947]

# Obter o preço do produto
if not df_produto.empty:
    preco_produto = df_produto['PRECO_38PERCENT'].iloc[0]
    result = f"O preço do produto 369947 é: R$ {preco_produto:.2f}"
else:
    result = "Produto 369947 não encontrado."

print(result)