# core/agents/supervisor_agent.py
import logging
from typing import List, Dict, Any # Import necessary types

from core.llm_base import BaseLLMAdapter
from core.agents.tool_agent import ToolAgent
from core.agents.code_gen_agent import CodeGenAgent

class SupervisorAgent:
    """
    Agente supervisor que roteia a consulta do usuário para o agente especialista apropriado.
    """
    def __init__(self, llm_adapter: BaseLLMAdapter):
        """
        Inicializa o supervisor, o ToolAgent, o CodeGenAgent e o LLM de roteamento.
        """
        self.logger = logging.getLogger(__name__)
        self.routing_llm = llm_adapter # Use o adaptador injetado
        self.tool_agent = ToolAgent(llm_adapter=llm_adapter)
        self.code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)
        self.logger.info("SupervisorAgent inicializado com os agentes especialistas.")

    def _build_routing_prompt(self, query: str) -> List[Dict[str, str]]:
        """
        Constrói o prompt para o LLM de roteamento decidir qual agente usar.
        Retorna uma lista de mensagens no formato esperado pela API do OpenAI.
        """
        system_message = {
            "role": "system",
            "content": "Você é um agente supervisor responsável por rotear consultas de usuários para o agente especialista correto."
        }
        user_message = {
            "role": "user",
            "content": f"""
            Você tem dois agentes especialistas disponíveis:
            1.  **ToolAgent**: Este agente usa um conjunto de ferramentas predefinidas para responder a perguntas simples sobre os dados, como procurar informações específicas (por exemplo, o preço de um produto) ou obter o esquema do banco de dados. É rápido e eficiente para consultas diretas.
            2.  **CodeGenAgent**: Este agente gera e executa código Python para responder a perguntas complexas que exigem análise de dados, agregações, cálculos ou visualizações (gráficos). É poderoso, mas mais lento.

            Sua tarefa é analisar a consulta do usuário e decidir qual agente é mais adequado.

            - Se a consulta for uma pergunta simples que pode ser respondida consultando informações diretas, encaminhe para o **ToolAgent**.
            - Se a consulta exigir análise complexa, cálculos, agregações ou a geração de um gráfico, encaminhe para o **CodeGenAgent**.

            Com base na consulta abaixo, qual agente deve ser usado? Responda com apenas uma palavra: "tool" ou "code".

            **Exemplos:**

            Consulta: "Qual o preço do produto 'Camisa Polo Azul'?"
            Resposta: tool

            Consulta: "Liste todas as categorias de produtos."
            Resposta: tool

            Consulta: "Qual a data da última venda do produto com ID 123?"
            Resposta: tool

            Consulta: "Mostre um gráfico de vendas por mês no último ano."
            Resposta: code

            Consulta: "Calcule a média de vendas por região."
            Resposta: code

            Consulta: "Qual o produto mais vendido no trimestre anterior e qual o seu faturamento total?"
            Resposta: code

            **Consulta do Usuário:** "{query}"
            """
        }
        return [system_message, user_message]

    def route_query(self, query: str) -> dict:
        """
        Analisa a consulta, roteia para o agente apropriado e retorna a resposta.
        """
        self.logger.info(f"Roteando a consulta: '{query}'")

        routing_messages = self._build_routing_prompt(query)
        
        # Call get_completion with messages and extract content
        llm_response = self.routing_llm.get_completion(messages=routing_messages)
        
        if "error" in llm_response:
            self.logger.error(f"Erro interno ao rotear a consulta: {llm_response['error']}")
            self.logger.warning("Não foi possível determinar o agente apropriado. Tentando com o ToolAgent.")
            return self.tool_agent.process_query(query)

        routing_decision = llm_response.get("content", "").strip().lower()

        self.logger.info(f"Decisão de roteamento: {routing_decision}")

        if "tool" in routing_decision:
            self.logger.info("Encaminhando para o ToolAgent.")
            return self.tool_agent.process_query(query)
        elif "code" in routing_decision:
            self.logger.info("Encaminhando para o CodeGenAgent.")
            return self.code_gen_agent.generate_and_execute_code(query)
        else:
            self.logger.warning(f"Decisão de roteamento inválida: '{routing_decision}'. Usando ToolAgent como padrão.")
            return self.tool_agent.process_query(query)