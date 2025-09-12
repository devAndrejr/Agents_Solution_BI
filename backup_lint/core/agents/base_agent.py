import logging
import re # Keep re for now, might be used elsewhere, but not for _convert_to_sql
import pandas as pd
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/agent.log",
    filemode="a",
)
logger = logging.getLogger("base_agent")

# Carrega as variáveis do arquivo .env
load_dotenv()


class BaseAgent:
    """Classe base para todos os agentes do sistema."""

    def __init__(self, session_id=None, node_client=None):
        """
        Inicializa o agente base.

        Args:
            session_id (str): ID da sessão para persistência de estado.
            node_client (object): Cliente para o servidor mssql-mcp-node.
        """
        self.session_id = session_id
        self.node_client = node_client
        logger.info(
            "Agente base inicializado. Sessão: %s, Client: %s",
            session_id,
            "Configurado" if self.node_client else "Não Configurado",
        )

    def process_query(self, query):
        """
        Processa uma consulta do usuário.
        This method now assumes that if node_client is used, the query is already SQL.
        """
        logger.info("Processando consulta: %s", query)
        if self.node_client:
            logger.info("Usando NodeMCPClient para processar a consulta SQL.")
            # Assuming 'query' is already a SQL query and no params are needed for this path
            return self._process_query_with_node_client(sql_query=query, query_params=None)
        logger.error(
            "Nenhum método de processamento disponível. Não é possível responder."
        )
        return {
            "type": "error",
            "content": "Não foi possível processar sua consulta no momento.",
            "source": "no_processing_method",
        }

    def _process_query_with_node_client(self, sql_query: str, query_params: list = None):
        """Processa uma consulta SQL usando o NodeMCPClient."""
        try:
            logger.info(
                "Executando SQL via NodeMCPClient: '%s' com params: %s",
                sql_query,
                query_params,
            )
            result_data = self.node_client.execute_sql(
                sql_query=sql_query, parameters=query_params
            )
            logger.debug("Resultado do NodeMCPClient: %s", result_data)

            if result_data and result_data.get("success"):
                df = pd.DataFrame(result_data.get("result", []))
                # Converte o DataFrame para uma lista de dicionários,
                # tratando valores nulos (NaN, NaT) como None.
                content_data = df.where(pd.notna(df), None).to_dict(orient="records")

                return {
                    "type": "data",
                    "content": content_data,
                    "source": "node_mcp_client",
                }

            error_info = result_data.get("error") if result_data else "No response"
            logger.error(
                "Erro retornado pelo NodeMCPClient: %s - Detalhes: %s",
                error_info,
                result_data.get("details") if result_data else "N/A",
            )
            return {
                "type": "error",
                "content": f"Erro ao processar consulta: {error_info}",
                "source": "node_mcp_client",
            }

        except Exception as e:
            logger.error(
                "Erro ao processar consulta com NodeMCPClient: %s", e, exc_info=True
            )
            return {
                "type": "error",
                "content": f"Erro inesperado ao processar consulta: {e}",
                "source": "node_mcp_client_exception",
            }