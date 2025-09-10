import logging
from typing import Literal, Any
import json
import plotly.io as pio

from langchain_core.messages import AIMessage, ToolMessage, BaseMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from core.agent_state import AgentState
from core.agents.caculinha_bi_agent import create_caculinha_bi_agent
from core.agents.code_gen_agent import CodeGenAgent
from core.config.settings import Settings
from core.connectivity.base import DatabaseAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphBuilder:
    """Encapsula a lógica de construção do grafo LangGraph com injeção de dependência."""

    def __init__(self, settings: Settings, db_adapter: DatabaseAdapter, code_gen_agent: CodeGenAgent, llm_adapter: Any):
        """
        Inicializa o construtor do grafo com as dependências necessárias.
        """
        self.settings = settings
        self.db_adapter = db_adapter
        self.code_gen_agent = code_gen_agent
        self.llm_adapter = llm_adapter
        self.bi_agent_runnable, bi_tools = create_caculinha_bi_agent(self.settings.PARQUET_DIR, self.code_gen_agent, self.llm_adapter)
        self.bi_tool_node = ToolNode(bi_tools)

    def bi_agent_node_func(self, state: AgentState) -> dict:
        """Executa o agente de BI."""
        logger.info("--- Nó do Agente de BI ---")
        agent_output = self.bi_agent_runnable.invoke(state)
        return agent_output

    def process_bi_tool_output_func(self, state: AgentState) -> dict:
        """Processa a saída de uma ferramenta de BI e atualiza o estado."""
        logger.info("--- Nó de Processamento da Saída da Ferramenta de BI ---")
        last_msg = state["messages"][-1]

        if not isinstance(last_msg, ToolMessage):
            return {}

        content = last_msg.content
        tool_name = last_msg.name

        formatted_output = ""

        if tool_name == "generate_and_execute_python_code":
            processed_content = None
            if isinstance(content, str):
                try:
                    processed_content = json.loads(content)
                except json.JSONDecodeError:
                    formatted_output = f"Saída da ferramenta de geração de código não é um JSON válido: {content}"
            elif isinstance(content, dict):
                processed_content = content

            if processed_content and isinstance(processed_content, dict):
                content_type = processed_content.get("type")
                output = processed_content.get("output")

                if content_type == "chart":
                    formatted_output = "Gráfico gerado com sucesso e disponível para visualização."
                    try:
                        fig = pio.from_json(output)
                        return {"messages": [AIMessage(content=formatted_output, additional_kwargs={"plotly_fig": fig})]}
                    except Exception as e:
                        logger.error(f"Erro ao desserializar a figura Plotly: {e}")
                        formatted_output = "Erro ao processar o gráfico gerado."
                elif content_type == "dataframe":
                    formatted_output = "Dados processados e disponíveis."
                    return {"messages": [AIMessage(content=formatted_output)], "retrieved_data": output}
                else:
                    formatted_output = f"Saída da ferramenta de geração de código com tipo desconhecido: {processed_content}"
            elif not formatted_output:
                formatted_output = f"Saída da ferramenta de geração de código não pôde ser processada. Tipo: {type(content)}, Conteúdo: {content}"
        else:
            formatted_output = f"Saída de ferramenta desconhecida: {tool_name} - {content}"

        return {"messages": [AIMessage(content=formatted_output)]}

    def route_from_bi_agent(self, state: AgentState) -> Literal["bi_tools", "__end__"]:
        """Decide se deve chamar as ferramentas de BI ou finalizar."""
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and not last_message.tool_calls:
            return "__end__"
        elif isinstance(last_message, BaseMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "bi_tools"
        return "__end__"

    def build(self):
        """Constrói e compila o grafo de execução do LangGraph."""
        workflow = StateGraph(AgentState)

        workflow.add_node("caculinha_bi_agent", self.bi_agent_node_func)
        workflow.add_node("bi_tools", self.bi_tool_node)
        workflow.add_node("process_bi_tool_output", self.process_bi_tool_output_func)

        workflow.set_entry_point("caculinha_bi_agent")

        workflow.add_conditional_edges(
            "caculinha_bi_agent",
            self.route_from_bi_agent,
            {"bi_tools": "bi_tools", "__end__": END},
        )

        workflow.add_edge("bi_tools", "process_bi_tool_output")
        workflow.add_edge("process_bi_tool_output", END)

        app = workflow.compile()
        logger.info("Grafo LangGraph compilado com sucesso com uma arquitetura simplificada!")
        return app