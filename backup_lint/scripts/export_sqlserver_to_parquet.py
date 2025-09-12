import logging
import os
import sys
import urllib.parse
from datetime import datetime

import pandas as pd
import pyodbc
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/export_sqlserver_to_parquet.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do banco (usando nomes padronizados)
server = os.getenv("DB_SERVER")
database = os.getenv("DB_DATABASE")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# Diretório de saída
PARQUET_DIR = os.path.join("data", "parquet")
os.makedirs(PARQUET_DIR, exist_ok=True)

# String de conexão pyodbc para teste
conn_string = (
    f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
    f"UID={username};PWD={password};TrustServerCertificate=yes;Encrypt=no;"
)

# Testa conexão antes de criar engine SQLAlchemy
try:
    logger.info(
        "Testando conexão com SQL Server: %s/%s usando driver '%s'...",
        server,
        database,
        driver,
    )
    conn = pyodbc.connect(conn_string, timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    conn.close()
    logger.info("[OK] Conexão bem-sucedida com o SQL Server!")
except Exception as e:
    logger.error("[ERRO] Falha ao conectar ao SQL Server: %s", e)
    sys.exit(1)

# String de conexão para SQLAlchemy usando odbc_connect
odbc_str = (
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"TrustServerCertificate=yes;"
    f"Encrypt=no;"
)
params = urllib.parse.quote_plus(odbc_str)
connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
logger.info(
    "String de conexão (parcial): mssql+pyodbc:///?odbc_connect=... "
    "(usando SERVER=%s, DATABASE=%s, DRIVER=%s)",
    server,
    database,
    driver,
)

# Cria engine SQLAlchemy
engine = create_engine(connection_string)


def export_all_tables_to_parquet():
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info("Tabelas encontradas: %s", tables)
        for table in tables:
            try:
                logger.info("Exportando tabela: %s", table)
                df = pd.read_sql_table(table, engine)
                parquet_path = os.path.join(PARQUET_DIR, f"{table}.parquet")
                df.to_parquet(parquet_path, index=False)
                logger.info(
                    "Tabela %s exportada para %s (%d linhas)",
                    table,
                    parquet_path,
                    len(df),
                )
            except Exception as e:
                logger.error("Erro ao exportar tabela %s: %s", table, e)
        logger.info("Exportação concluída.")
    except Exception as e:
        logger.error("Erro geral na exportação: %s", e)


if __name__ == "__main__":
    logger.info("Iniciando exportação SQL Server -> Parquet")
    export_all_tables_to_parquet()
    logger.info("Finalizado em %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
