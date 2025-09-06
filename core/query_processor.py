# core/query_processor.py
import logging
from core.agents.supervisor_agent import SupervisorAgent
from core.llm_base import BaseLLMAdapter
from core.llm_adapter import OpenAILLMAdapter # Importe a implementação concreta

class QueryProcessor:
    """
    Ponto de entrada principal para o processamento de consultas.
    Delega a tarefa para o SupervisorAgent para orquestração.
    """
    def __init__(self):
        """
        Inicializa o processador de consultas e o agente supervisor.
        """
        self.logger = logging.getLogger(__name__)
        self.llm_adapter: BaseLLMAdapter = OpenAILLMAdapter()
        self.supervisor = SupervisorAgent(llm_adapter=self.llm_adapter)
        self.logger.info("QueryProcessor inicializado e pronto para delegar ao SupervisorAgent.")

    def process_query(self, query: str) -> dict:
        """
        Processa a consulta do usuário, delegando-a diretamente ao SupervisorAgent.

        Args:
            query (str): A consulta do usuário.

        Returns:
            dict: O resultado do processamento pelo agente especialista apropriado.
        """
        self.logger.info(f'Delegando a consulta para o Supervisor: "{query}"')
        return self.supervisor.route_query(query)
