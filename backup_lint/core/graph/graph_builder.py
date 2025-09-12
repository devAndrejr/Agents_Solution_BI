'''
Construtor do StateGraph para a arquitetura avançada do Agent_BI.
Este módulo reescrito define a máquina de estados finitos que orquestra
o fluxo de tarefas, conectando os nós definidos em 'bi_agent_nodes.py'.
'''
import logging
from functools import partial
from langgraph.graph import StateGraph, END

from core.agent_state import AgentState
from core.llm_base import BaseLLMAdapter
from core.connectivity.base import DatabaseAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.agents import bi_agent_nodes

logger = logging.getLogger(__name__)

class GraphBuilder:
    '''
    Constrói e compila o grafo de execução do LangGraph, implementando a
    lógica da máquina de estados para o fluxo de BI.
    '''

    def __init__(self, llm_adapter: BaseLLMAdapter, db_adapter: DatabaseAdapter, code_gen_agent: CodeGenAgent):
        '''
        Inicializa o construtor com as dependências necessárias (injeção de dependência).
        '''
        self.llm_adapter = llm_adapter
        self.db_adapter = db_adapter
        self.code_gen_agent = code_gen_agent

    def _decide_after_intent_classification(self, state: AgentState) -> str:
        '''
        Aresta condicional que roteia o fluxo após a classificação da intenção.
        '''
        intent = state.get("intent")
        if intent == "gerar_grafico":
            return "clarify_requirements"
        elif intent == "consulta_sql_complexa":
            return "generate_sql_query"
        else: # resposta_simples ou fallback
            return "generate_sql_query" # Simplificado: sempre gera SQL por enquanto

    def _decide_after_clarification(self, state: AgentState) -> str:
        '''
        Aresta condicional que decide o fluxo após a verificação de requisitos.
        '''
        if state.get("clarification_needed"):
            return "format_final_response"  # Termina para pedir input ao usuário
        else:
            return "generate_sql_query"

    def build(self):
        '''
        Constrói, define as arestas e compila o StateGraph.
        '''
        workflow = StateGraph(AgentState)

        # Vincula as dependências aos nós usando functools.partial
        classify_intent_node = partial(bi_agent_nodes.classify_intent, llm_adapter=self.llm_adapter)
        generate_sql_query_node = partial(bi_agent_nodes.generate_sql_query, code_gen_agent=self.code_gen_agent)
        execute_query_node = partial(bi_agent_nodes.execute_query, db_adapter=self.db_adapter)

        # Adiciona os nós (estados) ao grafo
        workflow.add_node("classify_intent", classify_intent_node)
        workflow.add_node("clarify_requirements", bi_agent_nodes.clarify_requirements)
        workflow.add_node("generate_sql_query", generate_sql_query_node)
        workflow.add_node("execute_query", execute_query_node)
        workflow.add_node("generate_plotly_spec", bi_agent_nodes.generate_plotly_spec)
        workflow.add_node("format_final_response", bi_agent_nodes.format_final_response)

        # Define o ponto de entrada
        workflow.set_entry_point("classify_intent")

        # Adiciona as arestas (transições entre estados)
        workflow.add_conditional_edge(
            "classify_intent",
            self._decide_after_intent_classification,
            {
                "clarify_requirements": "clarify_requirements",
                "generate_sql_query": "generate_sql_query",
            }
        )
        workflow.add_conditional_edge(
            "clarify_requirements",
            self._decide_after_clarification,
            {
                "format_final_response": "format_final_response",
                "generate_sql_query": "generate_sql_query",
            }
        )
        workflow.add_edge("generate_sql_query", "execute_query")
        workflow.add_edge("execute_query", "generate_plotly_spec") # Simplificado: sempre tenta gerar gráfico
        workflow.add_edge("generate_plotly_spec", "format_final_response")
        
        # O nó final aponta para o fim do grafo
        workflow.add_edge("format_final_response", END)

        # Compila o grafo em uma aplicação executável
        app = workflow.compile()
        logger.info("Grafo LangGraph da arquitetura avançada compilado com sucesso!")
        return app