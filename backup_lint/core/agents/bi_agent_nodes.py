'''
Nós (estados) para o StateGraph da arquitetura avançada do Agent_BI.
Cada função representa um passo no fluxo de processamento da consulta.
As dependências (como adaptadores de LLM e DB) são injetadas pelo GraphBuilder.
'''
import logging
from typing import Dict, Any, List

from core.agent_state import AgentState
from core.llm_base import BaseLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.tools.data_tools import fetch_data_from_query
from core.connectivity.base import DatabaseAdapter

logger = logging.getLogger(__name__)

def classify_intent(state: AgentState, llm_adapter: BaseLLMAdapter) -> Dict[str, Any]:
    '''
    Classifica a intenção do usuário usando um LLM e extrai entidades.
    Atualiza o estado com o plano de ação.
    '''
    logger.info("Nó: classify_intent")
    user_query = state['messages'][-1].content
    
    prompt = f'''
    Você é um roteador inteligente. Analise a consulta do usuário e classifique a intenção principal.
    As intenções possíveis são:
    - 'gerar_grafico': O usuário quer uma visualização de dados (gráfico, plot, etc.).
    - 'consulta_sql_complexa': A pergunta requer uma consulta SQL com agregações, junções ou lógica complexa.
    - 'resposta_simples': A pergunta pode ser respondida com uma consulta SQL simples ou uma resposta direta.

    Extraia também as entidades principais da consulta, como métricas, dimensões e filtros.

    Consulta: "{user_query}"

    Responda em formato JSON com as chaves 'intent' e 'entities'.
    Exemplo:
    Consulta: "Mostre um gráfico de barras das vendas por região"
    {{
        "intent": "gerar_grafico",
        "entities": {{
            "metric": "vendas",
            "dimension": "região",
            "chart_type": "barras"
        }}
    }}
    '''
    
    response = llm_adapter.get_completion(messages=[{"role": "user", "content": prompt}])
    # Supondo que a resposta do LLM seja um JSON em 'content'
    plan = response.get("content", {}) 
    
    return {"plan": plan, "intent": plan.get("intent")}

def clarify_requirements(state: AgentState) -> Dict[str, Any]:
    '''
    Verifica se informações para um gráfico estão faltando e, se necessário,
    prepara um pedido de esclarecimento para o usuário.
    '''
    logger.info("Nó: clarify_requirements")
    plan = state.get("plan", {})
    entities = plan.get("entities", {})

    if state.get("intent") == "gerar_grafico":
        missing_info = []
        if not entities.get("dimension"):
            missing_info.append("dimensão (ex: por categoria, por data)")
        if not entities.get("metric"):
            missing_info.append("métrica (ex: total de vendas, quantidade)")
        if not entities.get("chart_type"):
            missing_info.append("tipo de gráfico (ex: barras, linhas, pizza)")

        if missing_info:
            options = {
                "message": f"Para gerar o gráfico, preciso que você especifique: {', '.join(missing_info)}.",
                "choices": {
                    "dimensions": ["Por Categoria", "Por Mês", "Por Região"],
                    "chart_types": ["Barras", "Linhas", "Pizza"]
                }
            }
            return {"clarification_needed": True, "clarification_options": options}

    return {"clarification_needed": False}

def generate_sql_query(state: AgentState, code_gen_agent: CodeGenAgent) -> Dict[str, Any]:
    '''
    Gera uma consulta SQL a partir da pergunta do usuário usando o CodeGenAgent.
    '''
    logger.info("Nó: generate_sql_query")
    user_query = state['messages'][-1].content
    
    # O CodeGenAgent é reutilizado para gerar SQL em vez de Python
    # Isso pode exigir um prompt específico para o CodeGenAgent
    response = code_gen_agent.generate_code(user_query, "sql") # Assumindo que o método aceita um tipo de código
    sql_query = response.get("output", "")

    return {"sql_query": sql_query}

def execute_query(state: AgentState, db_adapter: DatabaseAdapter) -> Dict[str, Any]:
    '''
    Executa a query SQL do estado usando a ferramenta fetch_data_from_query.
    '''
    logger.info("Nó: execute_query")
    sql_query = state.get("sql_query")
    if not sql_query:
        return {"raw_data": [{"error": "Nenhuma query SQL para executar."}]}
    
    # Chama a ferramenta diretamente, passando o adaptador
    raw_data = fetch_data_from_query.func(query=sql_query, db_adapter=db_adapter)
    
    return {"raw_data": raw_data}

def generate_plotly_spec(state: AgentState) -> Dict[str, Any]:
    '''
    Transforma os dados brutos do estado em uma especificação JSON para Plotly.
    '''
    logger.info("Nó: generate_plotly_spec")
    raw_data = state.get("raw_data")
    plan = state.get("plan", {})
    entities = plan.get("entities", {})

    if not raw_data or "error" in raw_data[0]:
        return {"final_response": "Não foi possível obter dados para gerar o gráfico."}

    # Lógica simplificada para criar a especificação do Plotly
    # Em um caso real, isso seria muito mais robusto
    dimension = entities.get("dimension")
    metric = entities.get("metric")
    chart_type = entities.get("chart_type", "bar")

    if not dimension or not metric:
        return {"final_response": "Não foi possível determinar a dimensão e a métrica para o gráfico."}

    x_values = [row[dimension] for row in raw_data]
    y_values = [row[metric] for row in raw_data]

    plotly_spec = {
        "data": [{
            "x": x_values,
            "y": y_values,
            "type": chart_type
        }],
        "layout": {
            "title": f"{metric.title()} por {dimension.title()}"
        }
    }
    
    return {"plotly_spec": plotly_spec}

def format_final_response(state: AgentState) -> Dict[str, Any]:
    '''
    Formata a resposta final para o usuário, seja texto, dados ou um gráfico.
    '''
    logger.info("Nó: format_final_response")
    if state.get("clarification_needed"):
        response = {
            "type": "clarification",
            "content": state.get("clarification_options")
        }
    elif state.get("plotly_spec"):
        response = {
            "type": "chart",
            "content": state.get("plotly_spec")
        }
    elif state.get("raw_data"):
        response = {
            "type": "data",
            "content": state.get("raw_data")
        }
    else:
        # Resposta padrão ou de erro
        response = {
            "type": "text",
            "content": "Não consegui processar sua solicitação. Tente novamente."
        }
        
    return {"final_response": response}