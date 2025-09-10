# core/connectivity/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class DatabaseAdapter(ABC):
    """
    Abstract Base Class for database adapters (Strategy Interface).
    Defines the common contract for all database connectivity.
    """
    @abstractmethod
    def connect(self) -> None:
        """Establishes a connection to the database."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Closes the database connection."""
        pass

    @abstractmethod
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Executes a query and returns the results as a list of dicts."""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Returns the database schema information."""
        pass