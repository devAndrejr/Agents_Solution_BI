
# scripts/create_parquet_sample.py
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

original_file_path = r"C:\Users\André\Documents\Agent_BI\data\parquet\ADMAT_REBUILT.parquet"
sample_file_path = r"C:\Users\André\Documents\Agent_BI\data\parquet\ADMAT_REBUILT_SAMPLE.parquet"

try:
    logger.info(f"Carregando o arquivo original: {original_file_path}")
    df_original = pd.read_parquet(original_file_path)
    logger.info(f"Arquivo original carregado. Shape: {df_original.shape}")

    # Criar uma amostra (por exemplo, as primeiras 1000 linhas)
    df_sample = df_original.head(1000)
    logger.info(f"Amostra criada. Shape: {df_sample.shape}")

    # Salvar a amostra
    df_sample.to_parquet(sample_file_path, index=False)
    logger.info(f"Amostra salva em: {sample_file_path}")

except FileNotFoundError:
    logger.error(f"Erro: Arquivo original não encontrado em {original_file_path}")
except Exception as e:
    logger.error(f"Erro ao criar a amostra do arquivo Parquet: {e}", exc_info=True)
