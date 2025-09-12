# core/connectivity/sql_server_adapter.py
from typing import Any, Dict, List
import pyodbc
from .base import DatabaseAdapter
from core.config.settings import Settings # Importa a nova classe de config

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
                self._connection = pyodbc.connect(self._settings.PYODBC_CONNECTION_STRING)
                self._cursor = self._connection.cursor()
                print("SQL Server connection successful.")
            except pyodbc.Error as ex:
                sqlstate = ex.args[0]
                print(f"SQL Server connection failed: {sqlstate}")
                raise

    def disconnect(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None
            print("SQL Server connection closed.")

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        if not self._cursor:
            self.connect()
        
        self._cursor.execute(query)
        columns = [column[0] for column in self._cursor.description]
        results = [dict(zip(columns, row)) for row in self._cursor.fetchall()]
        return results

    def get_schema(self) -> Dict[str, Any]:
        self.connect() # Ensure connection is established
        # Lógica para inspecionar o schema do banco de dados
        # (Exemplo simplificado)
        self._cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in self._cursor.fetchall()]
        return {"tables": tables}