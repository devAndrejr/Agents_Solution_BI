A seguir estão os cinco ficheiros Python que constituem o núcleo da nova arquitetura, gerados conforme solicitado.

**1. `core/tools/data_tools.py`**
```python
import logging
from typing import List, Dict, Any

# A anotação @tool do LangChain pode ser adicionada posteriormente, se necessário,
# mas manter a função simples promove o desacoplamento.

from core.connectivity.base import DatabaseAdapter

logger = logging.getLogger(__name__)

def fetch_data_from_query(query: str, db_adapter: DatabaseAdapter) -> List[Dict[str, Any]]:
    """
    Executa uma query SQL no banco de dados e retorna os dados brutos.

    Args:
        query: A string contendo a query SQL a ser executada.
        db_adapter: Uma instância de um adaptador de banco de dados que segue a
                    interface DatabaseAdapter para executar a query.

    Returns:
        Uma lista de dicionários, onde cada dicionário representa uma linha
        do resultado da query. Retorna uma lista vazia se não houver resultados
        ou um dicionário de erro em caso de falha.
    """
    logger.info(f"Executando a query SQL: {query}")
    try:
        result = db_adapter.execute_query(query)
        if result is None:
            logger.warning("A execução da query não retornou resultados.")
            return []
        logger.info(f"Query executada com sucesso. {len(result)} linhas retornadas.")
        return result
    except Exception as e:
        logger.error(f"Erro ao executar a query SQL: {e}", exc_info=True)
        # Retorna um formato de erro consistente que pode ser tratado pelo agente
        return [{"error": "Falha ao executar a consulta no banco de dados.", "details": str(e)}]
```

**2. `core/agents/bi_agent_nodes.py`**
```python
import logging
import json
from typing import Dict, Any

# As dependências (LLM, DatabaseAdapter, CodeGenAgent) são injetadas no estado do grafo.
from core.tools.data_tools import fetch_data_from_query

logger = logging.getLogger(__name__)

def classify_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """(Usa LLM). Classifica a intenção e extrai entidades da consulta do usuário."""
    logger.info("--- NODE: Classify Intent ---")
    query = state.get("initial_query")
    llm_adapter = state["llm_adapter"]

    prompt_template = f"""
    Você é um classificador de intenções para um sistema de BI. Sua tarefa é analisar a consulta do usuário e classificá-la em uma das seguintes categorias, retornando um JSON.

    1.  `gerar_grafico`: A consulta pede explicitamente por um gráfico, visualização, ou uma comparação que implique um gráfico (ex: "vendas por categoria").
    2.  `consulta_sql_complexa`: A consulta exige agregação, múltiplos joins, ou lógica complexa que é melhor traduzida para SQL (ex: "qual o produto mais vendido?").
    3.  `resposta_simples`: A consulta é uma busca direta que pode ser respondida com uma query simples (ex: "qual o preço do produto X?").

    Extraia também as seguintes entidades se presentes:
    - `metric`: A métrica a ser medida (ex: vendas, faturamento).
    - `dimension`: A dimensão pela qual agrupar (ex: categoria, região, tempo).
    - `chart_type`: O tipo de gráfico solicitado (ex: barras, linhas, pizza).

    Consulta: "{query}"

    Responda APENAS com o objeto JSON.
    """
    
    logger.info("Chamando LLM para classificação de intenção...")
    # llm_response = llm_adapter.get_completion(prompt_template)
    # plan = json.loads(llm_response['content'])

    # Lógica de mock para simular a resposta do LLM
    if "gráfico" in query.lower() or "vendas por" in query.lower() or "mostre" in query.lower():
        plan = {
            "intent": "gerar_grafico",
            "entities": {"metric": "vendas", "dimension": "categoria", "chart_type": "bar"}
        }
    elif "mais vendido" in query.lower() or "média de" in query.lower():
        plan = {"intent": "consulta_sql_complexa", "entities": {}}
    else:
        plan = {"intent": "resposta_simples", "entities": {}}

    logger.info(f"Intenção classificada: {plan['intent']}, Entidades: {plan['entities']}")
    state["plan"] = plan
    return state

def clarify_requirements(state: Dict[str, Any]) -> Dict[str, Any]:
    """(Código Determinístico). Verifica se faltam informações para um gráfico."""
    logger.info("--- NODE: Clarify Requirements ---")
    plan = state.get("plan", {})
    
    if plan.get("intent") != "gerar_grafico":
        state["clarification_needed"] = None
        return state

    entities = plan.get("entities", {})
    missing_info = []
    if not entities.get("dimension"):
        missing_info.append("dimensão (ex: por categoria, por mês)")
    if not entities.get("metric"):
        missing_info.append("métrica (ex: total de vendas, quantidade)")
    
    if missing_info:
        logger.info(f"Informações faltando para o gráfico: {missing_info}")
        clarification = {
            "message": f"Para gerar o gráfico, preciso que você especifique: {', '.join(missing_info)}.",
            "options": {
                "dimensão": ["Por Categoria", "Por Região", "Evolução Mensal"],
                "métrica": ["Total de Vendas", "Quantidade Vendida"]
            }
        }
        state["clarification_needed"] = clarification
        state["final_response"] = {"type": "clarification", "content": clarification}
    else:
        logger.info("Requisitos para o gráfico estão completos.")
        state["clarification_needed"] = None
    
    return state

def generate_sql_query(state: Dict[str, Any]) -> Dict[str, Any]:
    """(Usa LLM). Gera uma query SQL a partir da pergunta do usuário."""
    logger.info("--- NODE: Generate SQL Query ---")
    query = state.get("initial_query")
    code_gen_agent = state["code_gen_agent"]

    logger.info("Usando CodeGenAgent para gerar a query SQL...")
    # sql_query = code_gen_agent.generate_sql(query, db_schema)
    
    # Lógica de mock para simular a geração de SQL
    plan = state.get("plan", {})
    entities = plan.get("entities", {})
    if plan.get("intent") == "gerar_grafico":
        dimension = entities.get("dimension", "categoria")
        metric = entities.get("metric", "valor_total")
        sql_query = f"SELECT {dimension}, SUM({metric}) as total FROM vendas GROUP BY {dimension} ORDER BY total DESC;"
    else:
        sql_query = f"SELECT produto, faturamento_total FROM vendas ORDER BY faturamento_total DESC LIMIT 1;"

    logger.info(f"Query SQL gerada: {sql_query}")
    state["sql_query"] = sql_query
    return state

def execute_query(state: Dict[str, Any]) -> Dict[str, Any]:
    """(Código Determinístico). Executa a query SQL e armazena os dados."""
    logger.info("--- NODE: Execute Query ---")
    sql_query = state.get("sql_query")
    db_adapter = state["db_adapter"]

    if not sql_query:
        logger.warning("Nenhuma query SQL para executar.")
        state["raw_data"] = [{"error": "Nenhuma query SQL foi gerada."}]
        return state

    raw_data = fetch_data_from_query(sql_query, db_adapter)
    state["raw_data"] = raw_data
    logger.info(f"Dados brutos recebidos: {len(raw_data)} linhas.")
    return state

def generate_plotly_spec(state: Dict[str, Any]) -> Dict[str, Any]:
    """(Código Determinístico). Transforma dados brutos em uma especificação JSON do Plotly."""
    logger.info("--- NODE: Generate Plotly Spec ---")
    raw_data = state.get("raw_data")
    plan = state.get("plan", {})
    entities = plan.get("entities", {})

    if not raw_data or (isinstance(raw_data, list) and raw_data and "error" in raw_data[0]):
        logger.warning("Não há dados brutos ou ocorreu um erro na busca para gerar o gráfico.")
        state["plotly_spec"] = {"error": "Não foi possível gerar o gráfico pois a busca de dados falhou."}
        return state

    try:
        dimension = entities.get("dimension", list(raw_data[0].keys())[0])
        metric = entities.get("metric", list(raw_data[0].keys())[1])
        chart_type = entities.get("chart_type", "bar")

        x_values = [row[dimension] for row in raw_data]
        y_values = [row[list(raw_data[0].keys())[1]] for row in raw_data] # Use a key que de fato existe

        plotly_spec = {
            "data": [{"x": x_values, "y": y_values, "type": chart_type}],
            "layout": {
                "title": f"{str(metric).title()} por {str(dimension).title()}",
                "xaxis": {"title": str(dimension).title()},
                "yaxis": {"title": str(metric).title()}
            }
        }
        logger.info("Especificação Plotly JSON gerada com sucesso.")
        state["plotly_spec"] = plotly_spec
    except Exception as e:
        logger.error(f"Erro ao gerar especificação Plotly: {e}", exc_info=True)
        state["plotly_spec"] = {"error": f"Erro interno ao transformar dados em gráfico: {e}"}

    return state

def format_final_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """(Código Determinativo). Formata a resposta final para o usuário."""
    logger.info("--- NODE: Format Final Response ---")
    
    if state.get("final_response") and state["final_response"]["type"] == "clarification":
        return state

    if state.get("plotly_spec") and "error" not in state["plotly_spec"]:
        state["final_response"] = {"type": "chart", "content": state["plotly_spec"]}
    elif state.get("raw_data") and "error" not in state["raw_data"][0]:
        state["final_response"] = {"type": "data", "content": state["raw_data"]}
    else:
        error_details = state.get("raw_data", [{}])[0].get("details", "Erro desconhecido.")
        state["final_response"] = {"type": "text", "content": f"Não consegui processar sua solicitação. Detalhes: {error_details}"}
    
    logger.info(f"Resposta final formatada: tipo {state['final_response']['type']}")
    return state
```

**3. `core/graph/graph_builder.py`**
```python
import logging
from typing import TypedDict, Dict, Any, List, Literal, Optional

from langgraph.graph import StateGraph, END

from core.llm_base import BaseLLMAdapter
from core.connectivity.base import DatabaseAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.agents import bi_agent_nodes

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """Representa o estado do nosso grafo, passado entre os nós."""
    initial_query: str
    plan: Dict[str, Any]
    clarification_needed: Optional[Dict[str, Any]]
    sql_query: Optional[str]
    raw_data: Optional[List[Dict[str, Any]]]
    plotly_spec: Optional[Dict[str, Any]]
    final_response: Optional[Dict[str, Any]]
    # Dependências injetadas em tempo de execução
    llm_adapter: BaseLLMAdapter
    db_adapter: DatabaseAdapter
    code_gen_agent: CodeGenAgent

class GraphBuilder:
    """Constrói a máquina de estados (StateGraph) para o fluxo de BI."""

    def __init__(self, llm_adapter: BaseLLMAdapter, db_adapter: DatabaseAdapter, code_gen_agent: CodeGenAgent):
        """Inicializa o construtor com as dependências necessárias."""
        self.llm_adapter = llm_adapter
        self.db_adapter = db_adapter
        self.code_gen_agent = code_gen_agent
        logger.info("GraphBuilder inicializado com as dependências.")

    def _inject_dependencies(self, state: AgentState) -> AgentState:
        """Nó auxiliar para injetar dependências no estado inicial do grafo."""
        state['llm_adapter'] = self.llm_adapter
        state['db_adapter'] = self.db_adapter
        state['code_gen_agent'] = self.code_gen_agent
        return state

    def build(self):
        """Constrói e compila o grafo de execução do LangGraph."""
        workflow = StateGraph(AgentState)

        workflow.add_node("inject_dependencies", self._inject_dependencies)
        workflow.add_node("classify_intent", bi_agent_nodes.classify_intent)
        workflow.add_node("clarify_requirements", bi_agent_nodes.clarify_requirements)
        workflow.add_node("generate_sql_query", bi_agent_nodes.generate_sql_query)
        workflow.add_node("execute_query", bi_agent_nodes.execute_query)
        workflow.add_node("generate_plotly_spec", bi_agent_nodes.generate_plotly_spec)
        workflow.add_node("format_final_response", bi_agent_nodes.format_final_response)

        workflow.set_entry_point("inject_dependencies")
        workflow.add_edge("inject_dependencies", "classify_intent")

        workflow.add_conditional_edges(
            "classify_intent",
            self._decide_after_classification,
            {"clarify": "clarify_requirements", "generate_sql": "generate_sql_query"}
        )

        workflow.add_conditional_edges(
            "clarify_requirements",
            self._decide_after_clarification,
            {"format_response": "format_final_response", "generate_sql": "generate_sql_query"}
        )
        
        workflow.add_edge("generate_sql_query", "execute_query")

        workflow.add_conditional_edges(
            "execute_query",
            self._decide_after_execution,
            {"generate_spec": "generate_plotly_spec", "format_response": "format_final_response"}
        )

        workflow.add_edge("generate_plotly_spec", "format_final_response")
        workflow.add_edge("format_final_response", END)

        app = workflow.compile()
        logger.info("Grafo LangGraph da Arquitetura Avançada compilado com sucesso!")
        return app

    def _decide_after_classification(self, state: AgentState) -> Literal["clarify", "generate_sql"]:
        """Decide o próximo passo com base na intenção classificada."""
        intent = state.get("plan", {}).get("intent")
        logger.info(f"Decidindo rota após classificação. Intenção: {intent}")
        if intent == "gerar_grafico":
            return "clarify"
        return "generate_sql"

    def _decide_after_clarification(self, state: AgentState) -> Literal["format_response", "generate_sql"]:
        """Decide se os requisitos foram atendidos ou se a resposta deve ser enviada ao usuário."""
        if state.get("clarification_needed"):
            logger.info("Decidindo rota após clarificação: Requer interação do usuário.")
            return "format_response"
        logger.info("Decidindo rota após clarificação: Requisitos atendidos, gerando SQL.")
        return "generate_sql"

    def _decide_after_execution(self, state: AgentState) -> Literal["generate_spec", "format_response"]:
        """Decide se deve gerar um gráfico ou formatar os dados como resposta."""
        intent = state.get("plan", {}).get("intent")
        raw_data = state.get("raw_data")
        if intent == "gerar_grafico" and raw_data and not (isinstance(raw_data, list) and raw_data and "error" in raw_data[0]):
            logger.info("Decidindo rota após execução: Gerar especificação de gráfico.")
            return "generate_spec"
        logger.info("Decidindo rota após execução: Formatar resposta de dados/erro.")
        return "format_response"
```

**4. `main.py`**
```python
import uvicorn
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from core.graph.graph_builder import GraphBuilder, AgentState
from core.llm_adapter import OpenAILLMAdapter
from core.connectivity.sql_server_adapter import SQLServerAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.config.settings import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    query: str
    session_id: str

class QueryResponse(BaseModel):
    response: Dict[str, Any]

app = FastAPI(
    title="Agent_BI API Gateway",
    description="API para interagir com o sistema de agentes de BI baseado em LangGraph.",
    version="3.0.0"
)

agent_bi_graph = None

@app.on_event("startup")
def startup_event():
    """Inicializa as dependências e compila o grafo na inicialização da API."""
    global agent_bi_graph
    logger.info("Inicializando dependências e compilando o grafo...")
    try:
        llm_adapter = OpenAILLMAdapter(
            api_key=settings.OPENAI_API_KEY.get_secret_value(),
            model=settings.LLM_MODEL_NAME
        )
        db_adapter = SQLServerAdapter(
            server=settings.DB_SERVER,
            database=settings.DB_DATABASE,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD.get_secret_value()
        )
        code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)
        graph_builder = GraphBuilder(
            llm_adapter=llm_adapter,
            db_adapter=db_adapter,
            code_gen_agent=code_gen_agent
        )
        agent_bi_graph = graph_builder.build()
        logger.info("Dependências e grafo inicializados com sucesso.")
    except Exception as e:
        logger.critical(f"Falha fatal ao inicializar as dependências ou o grafo: {e}", exc_info=True)
        agent_bi_graph = None

@app.post("/api/v1/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """
    Recebe uma consulta do usuário, orquestra o fluxo de agentes através do StateGraph
    e retorna a resposta final.
    """
    if not agent_bi_graph:
        raise HTTPException(status_code=503, detail="Serviço indisponível: O grafo de agentes não está operacional.")

    logger.info(f"Recebida nova consulta da sessão {request.session_id}: '{request.query}'")
    
    try:
        initial_state: AgentState = {"initial_query": request.query}
        final_state = agent_bi_graph.invoke(initial_state)
        
        response_content = final_state.get("final_response", {
            "type": "error",
            "content": "Ocorreu um erro inesperado e não foi possível obter uma resposta."
        })

        logger.info(f"Enviando resposta final para a sessão {request.session_id}. Tipo: {response_content.get('type')}")
        return QueryResponse(response=response_content)

    except Exception as e:
        logger.error(f"Erro crítico ao invocar o grafo para a consulta '{request.query}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor ao processar a consulta.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**5. `streamlit_app.py`**
```python
import streamlit as st
import requests
import logging
import uuid

API_URL = "http://127.0.0.1:8000/api/v1/query"
PAGE_TITLE = "Agent_BI v3"
PAGE_ICON = "🤖"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.caption("A nova arquitetura de BI Conversacional com LangGraph")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": {"type": "text", "content": "Olá! Como posso ajudar você a analisar seus dados hoje?"}}]
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

@st.cache_data(show_spinner="Consultando o assistente de BI...")
def get_api_response(prompt: str, session_id: str):
    """Envia a consulta para a API FastAPI e retorna a resposta."""
    payload = {"query": prompt, "session_id": session_id}
    try:
        response = requests.post(API_URL, json=payload, timeout=180)
        response.raise_for_status()
        return response.json().get("response", {})
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao contatar a API: {e}")
        return {"type": "error", "content": f"Não foi possível conectar ao backend. Verifique se a API está rodando. Detalhes: {e}"}

def render_message(message_data):
    """Renderiza uma única mensagem na interface do chat."""
    role = message_data["role"]
    response_data = message_data["content"]
    
    with st.chat_message(role):
        msg_type = response_data.get("type")
        content = response_data.get("content")

        if msg_type == "chart":
            st.markdown("Aqui está o gráfico que você pediu:")
            st.plotly_chart(content, use_container_width=True)
        
        elif msg_type == "clarification":
            st.markdown(content.get("message"))
            options = content.get("options", {})
            cols = st.columns(len(options))
            idx = 0
            for key, values in options.items():
                with cols[idx]:
                    st.markdown(f"**Escolha um(a) {key}:**")
                    for value in values:
                        if st.button(value, key=f"{key}_{value}_{st.session_state.session_id}"):
                            refined_prompt = f"{st.session_state.last_query}, {value.lower()}"
                            st.session_state.user_input = refined_prompt
                            st.rerun()
                idx += 1

        elif msg_type == "data":
            st.markdown("Aqui estão os dados que encontrei:")
            st.dataframe(content, use_container_width=True)

        elif msg_type == "error":
            st.error(f"Ocorreu um erro: {content}")
        
        else:
            st.markdown(str(content))

for message in st.session_state.messages:
    render_message(message)

if st.session_state.user_input:
    prompt = st.session_state.user_input
    st.session_state.user_input = ""
else:
    prompt = st.chat_input("Faça sua pergunta...")

if prompt:
    st.session_state.last_query = prompt
    st.session_state.messages.append({"role": "user", "content": {"type": "text", "content": prompt}})
    api_response = get_api_response(prompt, st.session_state.session_id)
    st.session_state.messages.append({"role": "assistant", "content": api_response})
    st.rerun()
```
