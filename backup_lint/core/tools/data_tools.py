'''
Módulo contendo ferramentas de dados para serem usadas pelos agentes.
Cada ferramenta deve ser uma função simples e focada em uma única tarefa.
'''
import logging
from typing import List, Dict, Any
from langchain_core.tools import tool
from core.connectivity.base import DatabaseAdapter

logger = logging.getLogger(__name__)

@tool
def fetch_data_from_query(query: str, db_adapter: DatabaseAdapter) -> List[Dict[str, Any]]:
    '''
    Executa uma query SQL no banco de dados e retorna os dados brutos.

    Args:
        query: A string contendo a query SQL a ser executada.
        db_adapter: Uma instância de um adaptador de banco de dados que segue a
                    interface DatabaseAdapter para executar a query.

    Returns:
        Uma lista de dicionários, onde cada dicionário representa uma linha
        do resultado da query. Retorna uma lista vazia se não houver resultados
        ou um dicionário de erro em caso de falha.
    '''
    logger.info(f"Executando a query: {query}")
    try:
        # Assumindo que o db_adapter tem um método execute_query
        result = db_adapter.execute_query(query)
        if result is None:
            logger.warning("A execução da query não retornou resultados.")
            return []
        logger.info(f"Query executada com sucesso. {len(result)} linhas retornadas.")
        return result
    except Exception as e:
        logger.error(f"Erro ao executar a query SQL: {e}", exc_info=True)
        # Retornar um formato de erro consistente que pode ser tratado pelo agente
        return [{"error": "Falha ao executar a consulta no banco de dados.", "details": str(e)}]