import logging
from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from core.agent_state import AgentState
from core.agents.caculinha_bi_agent import (bi_tools,
                                            caculinha_bi_agent_runnable)
from core.agents.supervisor import RouteDecision, supervisor_router_runnable

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bi_tool_node = ToolNode(bi_tools)


def supervisor_node_func(state: AgentState) -> dict:
    """Decide qual o próximo passo a ser tomado pelo grafo."""
    logger.info("--- Supervisor Node ---")
    decision: RouteDecision = supervisor_router_runnable.invoke(
        {"messages": state["messages"]}
    )
    logger.info("--- Supervisor Decision: %s ---", decision.next_node)

    updates = {"route_decision": decision, "messages": []}

    if decision.next_node == "direct_response":
        content = decision.direct_response_content or "Não tenho uma resposta direta."
        updates["messages"] = [AIMessage(content=content, name="Supervisor")]
    elif decision.next_node == "clarification_request":
        content = decision.clarification_question or "Poderia esclarecer sua pergunta?"
        updates["messages"] = [AIMessage(content=content, name="Supervisor")]

    return updates


def bi_agent_node_func(state: AgentState) -> dict:
    """Executa o agente de BI."""
    logger.info("--- BI Agent Node ---")
    result = caculinha_bi_agent_runnable.invoke({"messages": state["messages"]})
    return {"messages": [result]}


def process_bi_tool_output_func(state: AgentState) -> dict:
    """Processa a saída de uma ferramenta de BI e atualiza o estado."""
    logger.info("--- Process BI Tool Output Node ---")
    last_msg = state["messages"][-1]
    updates = {}

    if not hasattr(last_msg, "name"):
        return updates

        content = last_msg.content
    tool_name = last_msg.name

    if tool_name == "execute_sql_query" and isinstance(content, dict):
        updates["retrieved_data"] = content.get("raw_data")
    elif tool_name == "generate_plotly_chart_code" and isinstance(content, str):
        if not content.startswith("Erro:"):
            updates["chart_code"] = content
    elif tool_name == "render_plotly_figure_from_code" and isinstance(content, dict):
        updates["plotly_fig"] = content.get("plotly_fig")

    return updates


def route_from_supervisor(
    state: AgentState,
) -> Literal["caculinha_bi_agent", "__end__"]:
    """Decide o caminho a partir do supervisor."""
    decision = state.get("route_decision")
    if decision and decision.next_node == "caculinha_bi_agent":
        return "caculinha_bi_agent"
    return "__end__"


def route_from_bi_agent(state: AgentState) -> Literal["bi_tools", "__end__"]:
    """Decide se deve chamar as ferramentas de BI ou finalizar."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "bi_tools"
    return "__end__"


def build_graph():
    """Constrói e compila o grafo de execução do LangGraph."""
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node_func)
    workflow.add_node("caculinha_bi_agent", bi_agent_node_func)
    workflow.add_node("bi_tools", bi_tool_node)
    workflow.add_node("process_bi_tool_output", process_bi_tool_output_func)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {"caculinha_bi_agent": "caculinha_bi_agent", "__end__": END},
    )
    workflow.add_conditional_edges(
        "caculinha_bi_agent",
        route_from_bi_agent,
        {"bi_tools": "bi_tools", "__end__": END},
    )

    workflow.add_edge("bi_tools", "process_bi_tool_output")
    workflow.add_edge("process_bi_tool_output", "caculinha_bi_agent")

    app = workflow.compile()
    logger.info("Grafo LangGraph compilado com sucesso!")
    return app
