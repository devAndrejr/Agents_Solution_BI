# tests/check_parquet_schema.py
import logging
import os
import sys
import pandas as pd

# Adiciona o diretório raiz ao path para resolver os imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from core.config.logging_config import setup_logging
from core.connectivity.parquet_adapter import ParquetAdapter

# Set up logging (optional for this script, but good practice)
setup_logging()
logger = logging.getLogger(__name__)

logger.info("--- Iniciando análise de esquema do arquivo Parquet ---")

file_path = r"C:\Users\André\Documents\Agent_BI\data\parquet\admatao.parquet"

try:
    parquet_adapter = ParquetAdapter(file_path=file_path)
    schema_str = parquet_adapter.get_schema()
    logger.info(f"Esquema do arquivo Parquet:\n{schema_str}")

    # Optionally, load a small sample to check actual data types more robustly
    # This might be redundant if get_schema is accurate, but good for verification
    df = pd.read_parquet(file_path)
    logger.info("\nTipos de dados inferidos pelo Pandas:")
    for col, dtype in df.dtypes.items():
        logger.info(f"  - {col}: {dtype}")

except FileNotFoundError:
    logger.error(f"Arquivo Parquet não encontrado: {file_path}")
except Exception as e:
    logger.error(f"Erro ao analisar o arquivo Parquet: {e}", exc_info=True)

logger.info("--- Análise de esquema do arquivo Parquet finalizada ---")
