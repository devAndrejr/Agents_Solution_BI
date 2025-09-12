`core/tools/data_tools.py`
```python
"""
Módulo contendo ferramentas de dados para serem usadas pelos agentes.
Cada ferramenta deve ser uma função simples e focada em uma única tarefa.
"""
import logging
from typing import List, Dict, Any
from langchain_core.tools import tool
from core.connectivity.base import DatabaseAdapter

logger = logging.getLogger(__name__)

@tool
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
```

`core/agents/bi_agent_nodes.py`
```python
"""
Nós (estados) para o StateGraph da arquitetura avançada do Agent_BI.
Cada função representa um passo no fluxo de processamento da consulta.
As dependências (como adaptadores de LLM e DB) são injetadas pelo GraphBuilder.
"""
import logging
from typing import Dict, Any, List

from core.agent_state import AgentState
from core.llm_base import BaseLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.tools.data_tools import fetch_data_from_query
from core.connectivity.base import DatabaseAdapter

logger = logging.getLogger(__name__)

def classify_intent(state: AgentState, llm_adapter: BaseLLMAdapter) -> Dict[str, Any]:
    """
    Classifica a intenção do usuário usando um LLM e extrai entidades.
    Atualiza o estado com o plano de ação.
    """
    logger.info("Nó: classify_intent")
    user_query = state['messages'][-1].content
    
    prompt = f"""
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
    """
    
    response = llm_adapter.get_completion(messages=[{"role": "user", "content": prompt}])
    # Supondo que a resposta do LLM seja um JSON em 'content'
    plan = response.get("content", {}) 
    
    return {"plan": plan, "intent": plan.get("intent")}

def clarify_requirements(state: AgentState) -> Dict[str, Any]:
    """
    Verifica se informações para um gráfico estão faltando e, se necessário,
    prepara um pedido de esclarecimento para o usuário.
    """
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
    """
    Gera uma consulta SQL a partir da pergunta do usuário usando o CodeGenAgent.
    """
    logger.info("Nó: generate_sql_query")
    user_query = state['messages'][-1].content
    
    # O CodeGenAgent é reutilizado para gerar SQL em vez de Python
    # Isso pode exigir um prompt específico para o CodeGenAgent
    response = code_gen_agent.generate_code(user_query, "sql") # Assumindo que o método aceita um tipo de código
    sql_query = response.get("output", "")

    return {"sql_query": sql_query}

def execute_query(state: AgentState, db_adapter: DatabaseAdapter) -> Dict[str, Any]:
    """
    Executa a query SQL do estado usando a ferramenta fetch_data_from_query.
    """
    logger.info("Nó: execute_query")
    sql_query = state.get("sql_query")
    if not sql_query:
        return {"raw_data": [{"error": "Nenhuma query SQL para executar."}]}
    
    # Chama a ferramenta diretamente, passando o adaptador
    raw_data = fetch_data_from_query.func(query=sql_query, db_adapter=db_adapter)
    
    return {"raw_data": raw_data}

def generate_plotly_spec(state: AgentState) -> Dict[str, Any]:
    """
    Transforma os dados brutos do estado em uma especificação JSON para Plotly.
    """
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
    """
    Formata a resposta final para o usuário, seja texto, dados ou um gráfico.
    """
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
```

`core/graph/graph_builder.py`
```python
"""
Construtor do StateGraph para a arquitetura avançada do Agent_BI.
Este módulo reescrito define a máquina de estados finitos que orquestra
o fluxo de tarefas, conectando os nós definidos em 'bi_agent_nodes.py'.
"""
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
    """
    Constrói e compila o grafo de execução do LangGraph, implementando a
    lógica da máquina de estados para o fluxo de BI.
    """

    def __init__(self, llm_adapter: BaseLLMAdapter, db_adapter: DatabaseAdapter, code_gen_agent: CodeGenAgent):
        """
        Inicializa o construtor com as dependências necessárias (injeção de dependência).
        """
        self.llm_adapter = llm_adapter
        self.db_adapter = db_adapter
        self.code_gen_agent = code_gen_agent

    def _decide_after_intent_classification(self, state: AgentState) -> str:
        """
        Aresta condicional que roteia o fluxo após a classificação da intenção.
        """
        intent = state.get("intent")
        if intent == "gerar_grafico":
            return "clarify_requirements"
        elif intent == "consulta_sql_complexa":
            return "generate_sql_query"
        else: # resposta_simples ou fallback
            return "generate_sql_query" # Simplificado: sempre gera SQL por enquanto

    def _decide_after_clarification(self, state: AgentState) -> str:
        """
        Aresta condicional que decide o fluxo após a verificação de requisitos.
        """
        if state.get("clarification_needed"):
            return "format_final_response"  # Termina para pedir input ao usuário
        else:
            return "generate_sql_query"

    def build(self):
        """
        Constrói, define as arestas e compila o StateGraph.
        """
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
```

`main.py`
```python
"""
API Gateway (Backend) para o Agent_BI usando FastAPI.
Este arquivo substitui a lógica anterior e serve como o ponto de entrada
principal para todas as interações do frontend.
"""
import uvicorn
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Importações dos componentes da nova arquitetura
from core.graph.graph_builder import GraphBuilder
from core.config.settings import settings
from core.llm_adapter import OpenAILLMAdapter
from core.connectivity.sql_server_adapter import SQLServerAdapter
from core.agents.code_gen_agent import CodeGenAgent # Supondo que ele exista e seja importável

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Modelos de Dados da API (Pydantic) ---
class QueryRequest(BaseModel):
    user_query: str
    session_id: str # Para gerenciar o estado da conversa

class QueryResponse(BaseModel):
    response: dict # A resposta final do grafo

# --- Inicialização da Aplicação e Dependências ---
app = FastAPI(
    title="Agent_BI - API Gateway",
    description="Backend FastAPI para a nova arquitetura com LangGraph.",
    version="3.0.0"
)

# Instanciação das dependências (pode ser otimizado com injeção de dependência do FastAPI)
# Para simplificar, instanciamos aqui. Em produção, use singletons ou `Depends`.
llm_adapter = OpenAILLMAdapter()
db_adapter = SQLServerAdapter(connection_string=settings.SQL_SERVER_CONNECTION_STRING)
code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)
graph_builder = GraphBuilder(llm_adapter=llm_adapter, db_adapter=db_adapter, code_gen_agent=code_gen_agent)
agent_graph = graph_builder.build()

# --- Endpoints da API ---
@app.post("/api/v1/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """
    Endpoint principal que recebe a consulta do usuário, invoca o grafo
    e retorna a resposta final.
    """
    logger.info(f"Recebida nova query para session_id='{request.session_id}': '{request.user_query}'")
    try:
        # O estado inicial é apenas a mensagem do usuário
        initial_state = {
            "messages": [{"role": "user", "content": request.user_query}]
        }
        
        # Invoca o grafo com o estado inicial
        final_state = agent_graph.invoke(initial_state)
        
        # A resposta final está na chave 'final_response' do estado
        response_content = final_state.get("final_response", {
            "type": "error",
            "content": "Ocorreu um erro inesperado no processamento do agente."
        })

        return QueryResponse(response=response_content)

    except Exception as e:
        logger.error(f"Erro crítico ao invocar o grafo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno no servidor do agente.")

@app.get("/status")
def status():
    return {"status": "Agent_BI API is running"}

# --- Execução da Aplicação ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

`streamlit_app.py`
```python
"""
Interface de Usuário (Frontend) para o Agent_BI, reescrita para ser um
cliente puro da API FastAPI.
"""
import streamlit as st
import requests
import uuid

# --- Configuração da Página ---
st.set_page_config(
    page_title="Agent_BI",
    page_icon="📊",
    layout="wide"
)
st.title("📊 Agent_BI - Assistente Inteligente")

# --- Constantes ---
API_URL = "http://127.0.0.1:8000/api/v1/query"

# --- Gerenciamento de Estado da Sessão ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Como posso ajudar você com seus dados hoje?"}]

# --- Funções de Interação com a API ---
def get_agent_response(user_query: str):
    """Envia a query para a API FastAPI e retorna a resposta."""
    try:
        payload = {
            "user_query": user_query,
            "session_id": st.session_state.session_id
        }
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()  # Lança exceção para status de erro HTTP
        return response.json().get("response", {})
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com o backend: {e}")
        return {"type": "error", "content": "Não foi possível conectar ao servidor do agente."}

# --- Renderização da Interface ---
# Exibe o histórico da conversa
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # O conteúdo agora é um dicionário com 'type' e 'content'
        response_data = msg.get("content")
        if isinstance(response_data, dict):
            response_type = response_data.get("type")
            content = response_data.get("content")
            
            if response_type == "chart":
                st.plotly_chart(content, use_container_width=True)
            elif response_type == "clarification":
                st.markdown(content.get("message"))
                # Renderiza botões para as opções de esclarecimento
                # Esta parte precisaria de uma lógica de callback mais complexa
                # para enviar a resposta do botão de volta para a API.
                # Por simplicidade, apenas exibimos as opções.
                for choice_type, choices in content.get("choices", {}).items():
                    st.write(f"**{choice_type.replace('_', ' ').title()}:**")
                    cols = st.columns(len(choices))
                    for i, choice in enumerate(choices):
                        if cols[i].button(choice):
                            # Em uma implementação real, este clique enviaria uma nova query
                            st.session_state.messages.append({"role": "user", "content": choice})
                            # Aqui, apenas adicionamos ao chat e rerodamos
                            st.rerun()

            else: # type 'data', 'text', 'error'
                st.write(content)
        else: # Formato antigo ou texto simples
            st.write(response_data)

# Input do usuário
if prompt := st.chat_input("Faça sua pergunta..."):
    # Adiciona e exibe a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Obtém e exibe a resposta do assistente
    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            agent_response = get_agent_response(prompt)
            
            # Adiciona a resposta completa ao histórico para renderização
            st.session_state.messages.append({"role": "assistant", "content": agent_response})
            
            # Renderiza a resposta imediatamente
            response_type = agent_response.get("type")
            content = agent_response.get("content")

            if response_type == "chart":
                st.plotly_chart(content, use_container_width=True)
            elif response_type == "clarification":
                st.markdown(content.get("message"))
                # Simplificado: Apenas mostra as opções, sem funcionalidade de clique aqui
                for choice_type, choices in content.get("choices", {}).items():
                    st.write(f"**{choice_type.replace('_', ' ').title()}:**")
                    for choice in choices:
                        st.button(choice, disabled=True) # Desabilitado para evitar loop
            else: # data, text, error
                st.write(content)
```
