# tests/verify_parquet_file.py
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

file_path = r"C:\Users\André\Documents\Agent_BI\data\parquet\ADMAT_REBUILT.parquet"

try:
    logger.info(f"Tentando carregar o arquivo Parquet: {file_path}")
    df = pd.read_parquet(file_path)
    logger.info(f"Arquivo carregado com sucesso! Shape: {df.shape}")
    logger.info(f"Colunas: {df.columns.tolist()}")
    logger.info(f"Primeiras 5 linhas:\n{df.head()}")

except FileNotFoundError:
    logger.error(f"Erro: Arquivo no encontrado em {file_path}")
except Exception as e:
    logger.error(f"Erro ao carregar o arquivo Parquet: {e}", exc_info=True)

logger.info("--- Verificao do arquivo Parquet finalizada ---")
