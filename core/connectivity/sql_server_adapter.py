# core/connectivity/sql_server_adapter.py
import logging
from typing import Any, Dict, List
import pyodbc
from .base import DatabaseAdapter
from core.config.settings import Settings # Importa a nova classe de config

logger = logging.getLogger(__name__)

class SQLServerAdapter(DatabaseAdapter):
    """Concrete implementation of the adapter for Microsoft SQL Server."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._connection = None
        self._cursor = None

    def connect(self) -> None:
        """Establishes connection using the centralized settings."""
        if not self._connection:
            try:
                logger.info("Attempting to connect to SQL Server...")
                self._connection = pyodbc.connect(self._settings.PYODBC_CONNECTION_STRING)
                self._cursor = self._connection.cursor()
                logger.info("SQL Server connection successful.")
            except pyodbc.Error as ex:
                sqlstate = ex.args[0]
                logger.error(f"SQL Server connection failed: {sqlstate}", exc_info=True)
                raise

    def disconnect(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("SQL Server connection closed.")

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        if not self._cursor:
            self.connect()
        
        logger.debug(f"Executing query: {query}")
        self._cursor.execute(query)
        columns = [column[0] for column in self._cursor.description]
        results = [dict(zip(columns, row)) for row in self._cursor.fetchall()]
        logger.debug(f"Query returned {len(results)} rows.")
        return results

    def get_schema(self) -> str:
        """
        Inspeciona o banco de dados e gera uma string DDL (CREATE TABLE)
        para as tabelas, que será usada como contexto para o LLM.
        """
        self.connect()  # Garante que a conexão está ativa
        logger.info("Iniciando a inspeção do esquema do banco de dados...")
        
        # Busca todas as tabelas de usuário no esquema 'dbo'
        tabelas = self._cursor.tables(schema='dbo', tableType='TABLE').fetchall()
        ddl_final = []

        for tabela_info in tabelas:
            nome_tabela = tabela_info.table_name
            logger.info(f"Inspecionando a tabela: {nome_tabela}")
            
            try:
                # Inicia a string CREATE TABLE
                ddl = f"""CREATE TABLE {nome_tabela} (
"""
                
                # Busca as colunas da tabela
                colunas = self._cursor.columns(table=nome_tabela).fetchall()
                colunas_ddl = []
                for coluna in colunas:
                    coluna_str = f"    {coluna.column_name} {coluna.type_name}"
                    # Adiciona o tamanho da coluna se aplicável
                    if coluna.column_size is not None and coluna.type_name.lower() in ['varchar', 'nvarchar', 'char']:
                        coluna_str += f"({coluna.column_size})"
                    colunas_ddl.append(coluna_str)
                
                ddl += ",\n".join(colunas_ddl)
                ddl += "\n);"
                ddl_final.append(ddl)

            except Exception as e:
                logger.error(f"Erro ao inspecionar a tabela {nome_tabela}: {e}")

        if not ddl_final:
            logger.warning("Nenhuma tabela encontrada ou erro ao gerar DDL.")
            return ""
            
        schema_string = "\n\n".join(ddl_final)
        logger.info(f"Esquema DDL gerado com sucesso:\n{schema_string}")
        return schema_string