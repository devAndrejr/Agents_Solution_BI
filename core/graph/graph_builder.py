"""
Construtor do StateGraph para a arquitetura avançada do Agent_BI.
Este módulo reescrito define a máquina de estados finitos que orquestra
o fluxo de tarefas, conectando os nós definidos em 'bi_agent_nodes.py'.
"""
import logging
from functools import partial
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

# Importações corrigidas baseadas na estrutura do projeto
from core.agent_state import AgentState
from core.llm_base import BaseLLMAdapter
from core.connectivity.parquet_adapter import ParquetAdapter
from core.agents.code_gen_agent import CodeGenAgent
# CORREÇÃO: Removida a importação da função inexistente.
from core.agents import bi_agent_nodes

logger = logging.getLogger(__name__)

class GraphBuilder:
    """
    Constrói e compila o grafo de execução do LangGraph, implementando a
    lógica da máquina de estados para o fluxo de BI.
    """

    def __init__(self, llm_adapter: BaseLLMAdapter, parquet_adapter: ParquetAdapter, code_gen_agent: CodeGenAgent):
        """
        Inicializa o construtor com as dependências necessárias (injeção de dependência).
        """
        self.llm_adapter = llm_adapter
        self.parquet_adapter = parquet_adapter
        self.code_gen_agent = code_gen_agent

    def _decide_after_intent_classification(self, state: AgentState) -> str:
        """
        Aresta condicional que roteia o fluxo após a classificação da intenção.
        """
        intent = state.get("intent")
        logger.info(f"Roteando com base na intenção: {intent}")
        if intent == "gerar_grafico":
            return "clarify_requirements"
        elif intent == "consulta_parquet_complexa":
            return "generate_parquet_query"
        else: # resposta_simples ou fallback
            return "generate_parquet_query"

    def _decide_after_clarification(self, state: AgentState) -> str:
        """
        Aresta condicional que decide o fluxo após a verificação de requisitos.
        """
        if state.get("clarification_needed"):
            logger.info("Esclarecimento necessário. Finalizando para obter input do usuário.")
            return "format_final_response"
        else:
            logger.info("Nenhum esclarecimento necessário. Prosseguindo para gerar filtros Parquet.")
            return "generate_parquet_query"

    def _decide_after_query_execution(self, state: AgentState) -> str:
        """
        Decide se deve gerar um gráfico ou formatar a resposta com base na intenção original.
        """
        intent = state.get("intent")
        logger.info(f"Decidindo após execução da query com intenção: {intent}")
        if intent == "gerar_grafico":
            return "generate_plotly_spec"
        else:
            return "format_final_response"

    def build(self):
        """
        Constrói, define as arestas e compila o StateGraph.
        """
        workflow = StateGraph(AgentState)

        # Vincula as dependências aos nós usando functools.partial para passar os adaptadores
        classify_intent_node = partial(bi_agent_nodes.classify_intent, llm_adapter=self.llm_adapter)
        generate_parquet_query_node = partial(bi_agent_nodes.generate_parquet_query, llm_adapter=self.llm_adapter, parquet_adapter=self.parquet_adapter)
        # CORREÇÃO: A função correta 'execute_query' de bi_agent_nodes é usada aqui.
        execute_query_node = partial(bi_agent_nodes.execute_query, parquet_adapter=self.parquet_adapter)

        # Adiciona os nós (estados) ao grafo
        workflow.add_node("classify_intent", classify_intent_node)
        workflow.add_node("clarify_requirements", bi_agent_nodes.clarify_requirements)
        workflow.add_node("generate_parquet_query", generate_parquet_query_node)
        # CORREÇÃO: O nó é adicionado com o nome correto, correspondendo à função.
        workflow.add_node("execute_query", execute_query_node)
        generate_plotly_spec_node = partial(bi_agent_nodes.generate_plotly_spec, llm_adapter=self.llm_adapter, code_gen_agent=self.code_gen_agent)
        workflow.add_node("generate_plotly_spec", generate_plotly_spec_node)
        workflow.add_node("format_final_response", bi_agent_nodes.format_final_response)

        # Define o ponto de entrada
        workflow.set_entry_point("classify_intent")

        # Adiciona as arestas (transições entre estados)
        workflow.add_conditional_edges(
            "classify_intent",
            self._decide_after_intent_classification,
            {
                "clarify_requirements": "clarify_requirements",
                "generate_parquet_query": "generate_parquet_query",
            }
        )
        workflow.add_conditional_edges(
            "clarify_requirements",
            self._decide_after_clarification,
            {
                "format_final_response": "format_final_response",
                "generate_parquet_query": "generate_parquet_query",
            }
        )
        workflow.add_edge("generate_parquet_query", "execute_query")
        workflow.add_conditional_edges(
            "execute_query",
            self._decide_after_query_execution,
            {
                "generate_plotly_spec": "generate_plotly_spec",
                "format_final_response": "format_final_response"
            }
        )
        workflow.add_edge("generate_plotly_spec", "format_final_response")
        
        # O nó final aponta para o fim do grafo
        workflow.add_edge("format_final_response", END)

        # Compila o grafo em uma aplicação executável
        app = workflow.compile()
        logger.info("Grafo LangGraph da arquitetura avançada compilado com sucesso!")
        return app
