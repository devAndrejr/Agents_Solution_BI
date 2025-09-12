import os
import pandas as pd
import re

def to_snake_case(name):
    """
    Converte um nome de coluna para snake_case.
    Exemplos:
    'NomeProduto' -> 'nome_produto'
    'NOME_PRODUTO' -> 'nome_produto'
    'Nome_Produto' -> 'nome_produto'
    'VENDA 30D' -> 'venda_30d'
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return s2.replace(' ', '_')

def standardize_parquet_columns(directory):
    """
    Padroniza os nomes das colunas de todos os arquivos Parquet em um diretório.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".parquet"):
            file_path = os.path.join(directory, filename)
            try:
                df = pd.read_parquet(file_path)
                
                # Renomeia as colunas
                original_columns = df.columns.tolist()
                df.columns = [to_snake_case(col) for col in original_columns]
                
                # Salva o arquivo com as colunas renomeadas
                df.to_parquet(file_path, index=False)
                
                print(f"Colunas do arquivo '{filename}' padronizadas com sucesso.")
                
            except Exception as e:
                print(f"Erro ao processar o arquivo '{filename}': {e}")

if __name__ == "__main__":
    parquet_dir = os.path.join(os.getcwd(), "data", "parquet_cleaned")
    print(f"Iniciando a padronização de colunas no diretório: {parquet_dir}")
    standardize_parquet_columns(parquet_dir)
    print("Padronização concluída.")
