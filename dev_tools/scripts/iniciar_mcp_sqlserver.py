import argparse
import json
import logging
import os
import sys
from pathlib import Path

import pyodbc
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path para importações
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# Configuração de logging
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "mcp_setup.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("McpSqlSetup")


class McpSqlSetup:
    """
    Configura o ambiente e o banco de dados SQL Server para o MCP.
    """

    def __init__(self, skip_sql=False):
        self.db_vars = {}
        self.skip_sql = skip_sql

    def _load_config(self):
        """Carrega a configuração do banco de dados do arquivo .env."""
        load_dotenv()
        required = [
            "MSSQL_SERVER",
            "MSSQL_DATABASE",
            "MSSQL_USER",
            "MSSQL_PASSWORD",
            "DB_DRIVER",
        ]
        self.db_vars = {var: os.getenv(var) for var in required}
        missing = [k for k, v in self.db_vars.items() if not v]
        if missing:
            logger.error(
                "Variáveis de ambiente ausentes no .env: %s", ", ".join(missing)
            )
            return False
        logger.info("Configuração do banco de dados carregada do .env.")
        return True

    def _create_config_file(self):
        """Cria o arquivo de configuração JSON para o MCP SQL Server."""
        config_path = ROOT_DIR / "data" / "sqlserver_mcp_config.json"
        config = {
            "connection": {
                "server": self.db_vars["MSSQL_SERVER"],
                "database": self.db_vars["MSSQL_DATABASE"],
                "username": self.db_vars["MSSQL_USER"],
                "password": self.db_vars["MSSQL_PASSWORD"],
                "driver": self.db_vars["DB_DRIVER"],
                "trust_server_certificate": "yes",
            },
            "processing": {
                "max_parallel_queries": 4,
                "timeout_seconds": 30,
                "use_stored_procedures": True,
                "use_partitioning": True,
            },
            "stored_procedures": {
                "process_query": "sp_mcp_process_query",
                "get_sales_data": "sp_mcp_get_sales_data",
                "get_product_data": "sp_mcp_get_product_data",
                "get_category_data": "sp_mcp_get_category_data",
            },
        }
        try:
            with config_path.open("w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            logger.info("Arquivo de configuração criado: %s", config_path)
            return True
        except IOError as e:
            logger.error("Falha ao criar arquivo de configuração: %s", e)
            return False

    def _test_connection(self):
        """Testa a conexão com o SQL Server."""
        try:
            conn_string = (
                f"DRIVER={{{self.db_vars['DB_DRIVER']}}};"
                f"SERVER={self.db_vars['MSSQL_SERVER']};"
                f"DATABASE={self.db_vars['MSSQL_DATABASE']};"
                f"UID={self.db_vars['MSSQL_USER']};"
                f"PWD={self.db_vars['MSSQL_PASSWORD']};"
                "TrustServerCertificate=yes;"
            )
            with pyodbc.connect(conn_string, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()[0]
                logger.info("Conexão com SQL Server estabelecida.")
                logger.info("Versão do SQL Server: %s...", version[:50])
            return True
        except pyodbc.Error as e:
            logger.error("Erro de PyODBC ao conectar ao SQL Server: %s", e)
            return False

    def _execute_sql_script(self):
        """Executa o script SQL para configurar as stored procedures."""
        script_path = ROOT_DIR / "scripts" / "setup_mcp_sqlserver.sql"
        if not script_path.exists():
            logger.error("Script SQL não encontrado em: %s", script_path)
            return False

        try:
            with script_path.open("r", encoding="utf-8") as f:
                script = f.read()

            script = script.replace(
                "USE [seu_banco_de_dados];", f"USE [{self.db_vars['MSSQL_DATABASE']}];"
            )

            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                batches = script.split("GO")
                for batch in batches:
                    if batch.strip():
                        cursor.execute(batch)
                conn.commit()
            logger.info("Script SQL de setup executado com sucesso.")
            return True
        except (pyodbc.Error, IOError) as e:
            logger.error("Erro ao executar script SQL: %s", e)
            return False

    def _get_db_connection(self):
        """Retorna uma nova conexão com o banco de dados."""
        conn_string = (
            f"DRIVER={{{self.db_vars['DB_DRIVER']}}};"
            f"SERVER={self.db_vars['MSSQL_SERVER']};"
            f"DATABASE={self.db_vars['MSSQL_DATABASE']};"
            f"UID={self.db_vars['MSSQL_USER']};"
            f"PWD={self.db_vars['MSSQL_PASSWORD']};"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_string, autocommit=False)

    def run(self):
        """Executa o processo de configuração completo."""
        logger.info("Iniciando configuração do MCP para SQL Server...")
        if not self._load_config() or not self._test_connection():
            logger.critical(
                "Configuração abortada devido a erro de conexão ou de variáveis."
            )
            return

        if not self._create_config_file():
            logger.critical(
                "Configuração abortada devido a erro na criação do arquivo."
            )
            return

        if self.skip_sql:
            logger.info("Execução do script SQL pulada conforme solicitado.")
        else:
            if not self._execute_sql_script():
                logger.error(
                    "Falha ao executar script SQL. A configuração pode estar incompleta."
                )
            else:
                logger.info("Script SQL executado com sucesso.")

        logger.info("Configuração do MCP para SQL Server concluída com sucesso!")


def main():
    parser = argparse.ArgumentParser(description="Configuração do MCP para SQL Server")
    parser.add_argument(
        "--skip-sql", action="store_true", help="Pular a execução do script SQL"
    )
    args = parser.parse_args()

    setup = McpSqlSetup(skip_sql=args.skip_sql)
    setup.run()


if __name__ == "__main__":
    main()
