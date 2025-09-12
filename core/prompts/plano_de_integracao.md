Plano de Integração Completo: Agent_BI 3.0De: Engenheiro de Integração de Software SêniorAssunto: Implementação da nova arquitetura com LangGraph, FastAPI e Streamlit desacoplado.Parte 1: Código Corrigido e Pronto para IntegraçãoAnalisei os cinco ficheiros da nova arquitetura e ajustei todas as declarações de import para corresponderem perfeitamente à estrutura do seu projeto, conforme detalhado no relatorio_completo.md.Ficheiro 1: core/tools/data_tools.pyEste ficheiro foi simplificado para conter apenas a ferramenta de execução de queries, isolando a interação com a base de dados."""
Módulo de ferramentas de dados para o Agent_BI.
Estas ferramentas são componentes simples e reutilizáveis que os agentes podem executar.
"""
import logging
from typing import List, Dict, Any

from langchain_core.tools import tool

# Importação corrigida para a interface do adaptador de base de dados
from core.connectivity.base import DatabaseAdapter

logger = logging.getLogger(__name__)

@tool
def fetch_data_from_query(query: str, db_adapter: DatabaseAdapter) -> List[Dict[str, Any]]:
    """
    Ferramenta que recebe uma query SQL, a executa usando o DatabaseAdapter injetado,
    e retorna os dados brutos como uma lista de dicionários.
    """
    logger.info(f"Executando a query: {query}")
    try:
        results = db_adapter.execute_query(query)
        logger.info(f"Query executada com sucesso. {len(results)} linhas retornadas.")
        return results
    except Exception as e:
        logger.error(f"Erro ao executar a query na ferramenta: {e}", exc_info=True)
        return [{"error": "Falha ao executar a consulta no banco de dados.", "details": str(e)}]
Ficheiro 2: core/agents/bi_agent_nodes.py (Ficheiro Novo)Este novo ficheiro contém a lógica para cada nó (estado) da nossa Máquina de Estados, mantendo o graph_builder limpo e focado na orquestração."""
Nós (estados) para o StateGraph da arquitetura avançada do Agent_BI.
Cada função representa um passo no fluxo de processamento da consulta.
"""
import logging
import json
from typing import Dict, Any

# Importações corrigidas baseadas na estrutura completa do projeto
from core.agent_state import AgentState
from core.llm_base import BaseLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.tools.data_tools import fetch_data_from_query
from core.connectivity.base import DatabaseAdapter

logger = logging.getLogger(__name__)

def classify_intent(state: AgentState, llm_adapter: BaseLLMAdapter) -> Dict[str, Any]:
    """
    Classifica a intenção do utilizador usando um LLM e extrai entidades.
    Atualiza o estado com o plano de ação.
    """
    logger.info("Nó: classify_intent")
    user_query = state['messages'][-1]['content']

    # Este prompt é a inteligência extraída do antigo supervisor_agent.py
    prompt = f"""
    Analise a consulta do utilizador e classifique a intenção principal.
    Responda em formato JSON com 'intent' e 'entities'.
    Intenções possíveis: 'gerar_grafico', 'consulta_sql_complexa', 'resposta_simples'.

    Consulta: "{user_query}"
    """
    
    response_dict = llm_adapter.get_completion(messages=[{"role": "user", "content": prompt}])
    plan_str = response_dict.get("content", "{}")
    
    try:
        plan = json.loads(plan_str)
    except json.JSONDecodeError:
        plan = {"intent": "resposta_simples", "entities": {}}

    return {"plan": plan, "intent": plan.get("intent")}

def clarify_requirements(state: AgentState) -> Dict[str, Any]:
    """
    Verifica se informações para um gráfico estão em falta.
    """
    logger.info("Nó: clarify_requirements")
    plan = state.get("plan", {})
    entities = plan.get("entities", {})

    if state.get("intent") == "gerar_grafico":
        missing_info = []
        if not entities.get("dimension"): missing_info.append("dimensão")
        if not entities.get("metric"): missing_info.append("métrica")
        
        if missing_info:
            options = {
                "message": f"Para gerar o gráfico, preciso que especifique: {', '.join(missing_info)}.",
                "choices": { "dimensions": ["Por Categoria", "Por Mês"], "chart_types": ["Barras", "Linhas"] }
            }
            return {"clarification_needed": True, "clarification_options": options}

    return {"clarification_needed": False}

def generate_sql_query(state: AgentState, code_gen_agent: CodeGenAgent) -> Dict[str, Any]:
    """
    Gera uma consulta SQL a partir da pergunta do utilizador.
    """
    logger.info("Nó: generate_sql_query")
    user_query = state['messages'][-1]['content']
    response = code_gen_agent.generate_and_execute_code(user_query, execute=False)
    sql_query = response.get("output", "")
    return {"sql_query": sql_query}

def execute_query(state: AgentState, db_adapter: DatabaseAdapter) -> Dict[str, Any]:
    """
    Executa a query SQL do estado.
    """
    logger.info("Nó: execute_query")
    sql_query = state.get("sql_query")
    if not sql_query:
        return {"raw_data": [{"error": "Nenhuma query SQL para executar."}]}
    raw_data = fetch_data_from_query(query=sql_query, db_adapter=db_adapter)
    return {"raw_data": raw_data}

def generate_plotly_spec(state: AgentState) -> Dict[str, Any]:
    """
    Transforma os dados brutos numa especificação JSON para Plotly.
    """
    logger.info("Nó: generate_plotly_spec")
    raw_data = state.get("raw_data")
    if not raw_data or (isinstance(raw_data, list) and raw_data and "error" in raw_data[0]):
        return {"final_response": "Não foi possível obter dados para gerar o gráfico."}

    try:
        # Lógica simplificada para criar a especificação do Plotly
        if not raw_data: return {"final_response": "Nenhum dado para visualizar."}
        keys = list(raw_data[0].keys())
        dimension, metric = keys[0], keys[1]
        x_values = [row[dimension] for row in raw_data]
        y_values = [row[metric] for row in raw_data]

        plotly_spec = {
            "data": [{"x": x_values, "y": y_values, "type": "bar"}],
            "layout": {"title": f"{str(metric).title()} por {str(dimension).title()}"}
        }
        return {"plotly_spec": plotly_spec}
    except Exception as e:
        logger.error(f"Erro ao gerar especificação Plotly: {e}")
        return {"final_response": f"Não consegui gerar o gráfico."}

def format_final_response(state: AgentState) -> Dict[str, Any]:
    """
    Formata a resposta final para o utilizador.
    """
    logger.info("Nó: format_final_response")
    if state.get("clarification_needed"):
        response = {"type": "clarification", "content": state.get("clarification_options")}
    elif state.get("plotly_spec"):
        response = {"type": "chart", "content": state.get("plotly_spec")}
    elif state.get("raw_data"):
        response = {"type": "data", "content": state.get("raw_data")}
    else:
        response = {"type": "text", "content": "Não consegui processar a sua solicitação."}
        
    final_messages = state['messages'] + [{"role": "assistant", "content": response}]
    return {"messages": final_messages}
Ficheiro 3: core/graph/graph_builder.pyEste ficheiro foi reescrito para construir a Máquina de Estados, orquestrando os nós de bi_agent_nodes.py."""
Construtor do StateGraph para a arquitetura avançada do Agent_BI.
"""
import logging
from functools import partial
from langgraph.graph import StateGraph, END

# Importações corrigidas baseadas na estrutura do projeto
from core.agent_state import AgentState
from core.llm_base import BaseLLMAdapter
from core.connectivity.base import DatabaseAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.agents import bi_agent_nodes

logger = logging.getLogger(__name__)

class GraphBuilder:
    """
    Constrói e compila o grafo de execução do LangGraph.
    """
    def __init__(self, llm_adapter: BaseLLMAdapter, db_adapter: DatabaseAdapter, code_gen_agent: CodeGenAgent):
        self.llm_adapter = llm_adapter
        self.db_adapter = db_adapter
        self.code_gen_agent = code_gen_agent

    def _decide_after_intent_classification(self, state: AgentState) -> str:
        """Aresta condicional que roteia o fluxo após a classificação da intenção."""
        if state.get("intent") == "gerar_grafico":
            return "clarify_requirements"
        return "generate_sql_query"

    def _decide_after_clarification(self, state: AgentState) -> str:
        """Decide o fluxo após a verificação de requisitos."""
        return "format_final_response" if state.get("clarification_needed") else "generate_sql_query"

    def _decide_after_execution(self, state: AgentState) -> str:
        """Decide se deve gerar um gráfico ou formatar a resposta."""
        return "generate_plotly_spec" if state.get("intent") == "gerar_grafico" else "format_final_response"

    def build(self):
        """Constrói, define as arestas e compila o StateGraph."""
        workflow = StateGraph(AgentState)

        # Vincula as dependências aos nós que as necessitam
        classify_intent_node = partial(bi_agent_nodes.classify_intent, llm_adapter=self.llm_adapter)
        generate_sql_query_node = partial(bi_agent_nodes.generate_sql_query, code_gen_agent=self.code_gen_agent)
        execute_query_node = partial(bi_agent_nodes.execute_query, db_adapter=self.db_adapter)

        # Adiciona os nós
        workflow.add_node("classify_intent", classify_intent_node)
        workflow.add_node("clarify_requirements", bi_agent_nodes.clarify_requirements)
        workflow.add_node("generate_sql_query", generate_sql_query_node)
        workflow.add_node("execute_query", execute_query_node)
        workflow.add_node("generate_plotly_spec", bi_agent_nodes.generate_plotly_spec)
        workflow.add_node("format_final_response", bi_agent_nodes.format_final_response)

        # Define as arestas
        workflow.set_entry_point("classify_intent")
        workflow.add_conditional_edge("classify_intent", self._decide_after_intent_classification)
        workflow.add_conditional_edge("clarify_requirements", self._decide_after_clarification)
        workflow.add_edge("generate_sql_query", "execute_query")
        workflow.add_conditional_edge("execute_query", self._decide_after_execution)
        workflow.add_edge("generate_plotly_spec", "format_final_response")
        workflow.add_edge("format_final_response", END)

        app = workflow.compile()
        logger.info("Grafo LangGraph da arquitetura avançada compilado com sucesso!")
        return app
Ficheiro 4: main.py (na raiz do projeto)Este ficheiro substitui o main.py antigo e a API Flask, tornando-se o único backend."""
API Gateway (Backend) para o Agent_BI usando FastAPI.
"""
import uvicorn
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

# Importações corrigidas baseadas na estrutura completa do projeto
from core.graph.graph_builder import GraphBuilder
from core.config.settings import settings
from core.llm_adapter import OpenAILLMAdapter
from core.connectivity.sql_server_adapter import SQLServerAdapter
from core.agents.code_gen_agent import CodeGenAgent

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Modelos Pydantic para a API ---
class QueryRequest(BaseModel):
    user_query: str
    session_id: str
    messages: List[Dict[str, Any]]

class QueryResponse(BaseModel):
    response: dict

# --- Inicialização da Aplicação ---
app = FastAPI(title="Agent_BI - API Gateway", version="3.0.0")

# Instanciação das dependências
llm_adapter = OpenAILLMAdapter(api_key=settings.OPENAI_API_KEY.get_secret_value())
db_adapter = SQLServerAdapter(connection_string=settings.SQL_SERVER_CONNECTION_STRING)
code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)
graph_builder = GraphBuilder(llm_adapter=llm_adapter, db_adapter=db_adapter, code_gen_agent=code_gen_agent)
agent_graph = graph_builder.build()

# --- Endpoints ---
@app.post("/api/v1/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """
    Endpoint principal que recebe a consulta, invoca o grafo e retorna a resposta.
    """
    logger.info(f"Recebida query para session_id='{request.session_id}': '{request.user_query}'")
    try:
        initial_state = {"messages": request.messages}
        final_state = agent_graph.invoke(initial_state)
        response_content = final_state['messages'][-1]['content']
        return QueryResponse(response=response_content)
    except Exception as e:
        logger.error(f"Erro crítico ao invocar o grafo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno no servidor do agente.")

@app.get("/status")
def status():
    return {"status": "Agent_BI API is running"}

# --- Execução ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
Ficheiro 5: streamlit_app.py (na raiz do projeto)Este ficheiro foi reescrito para ser um cliente puro da API FastAPI, sem lógica de negócio."""
Interface de Utilizador (Frontend) para o Agent_BI.
"""
import streamlit as st
import requests
import uuid

# --- Configuração da Página ---
st.set_page_config(page_title="Agent_BI", page_icon="📊", layout="wide")
st.title("📊 Agent_BI - Assistente Inteligente")

# --- Constantes e Estado da Sessão ---
API_URL = "[http://127.0.0.1:8000/api/v1/query](http://127.0.0.1:8000/api/v1/query)"

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": {"type": "text", "content": "Olá! Como posso ajudar com os seus dados hoje?"}}]

# --- Funções de Interação ---
def handle_agent_interaction(user_input: str):
    """Envia a mensagem do utilizador para a API e processa a resposta."""
    st.session_state.messages.append({"role": "user", "content": {"type": "text", "content": user_input}})
    
    try:
        payload = {
            "user_query": user_input,
            "session_id": st.session_state.session_id,
            "messages": st.session_state.messages
        }
        with st.spinner("A processar..."):
            response = requests.post(API_URL, json=payload, timeout=60)
            response.raise_for_status()
            agent_response = response.json().get("response", {})
            st.session_state.messages.append({"role": "assistant", "content": agent_response})
    except requests.exceptions.RequestException as e:
        error_content = {"type": "error", "content": f"Não foi possível conectar ao servidor do agente: {e}"}
        st.session_state.messages.append({"role": "assistant", "content": error_content})

# --- Renderização da Interface ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        response_data = msg.get("content", {})
        response_type = response_data.get("type", "text")
        content = response_data.get("content", str(response_data))
        
        if response_type == "chart":
            st.plotly_chart(content, use_container_width=True)
        elif response_type == "clarification":
            st.markdown(content.get("message"))
            choices = content.get("choices", {})
            for choice_category, choice_list in choices.items():
                for choice in choice_list:
                    if st.button(choice, key=f"btn_{choice}_{uuid.uuid4()}"):
                        handle_agent_interaction(choice)
                        st.rerun()
        else:
            st.write(content)

if prompt := st.chat_input("Faça a sua pergunta..."):
    handle_agent_interaction(prompt)
    st.rerun()

Parte 2: Checklist de ImplementaçãoSiga estes passos para implementar a nova arquitetura de forma segura.✅ 1. Preparação (Backup)[ ] Git Commit: Antes de qualquer alteração, faça um commit do estado atual do seu projeto.git add .
git commit -m "Backup: Estado anterior à refatoração da arquitetura LangGraph"
[ ] Backup Manual (Opcional): Faça uma cópia de segurança manual dos 5 ficheiros que serão substituídos e dos que serão eliminados.✅ 2. Limpeza (Remoção da Arquitetura Antiga)[ ] Elimine os Ficheiros e Pastas Redundantes: Vá ao seu projeto e elimine com segurança os seguintes itens.Ficheiros:core/query_processor.pycore/agents/supervisor_agent.pycore/orchestration/supervisor.pytests/test_supervisor_agent.pytests/test_real_queries.py (será substituído por novos testes de API)run_app.py, run_refactored_app.py na raiz do projeto.Pastas:core/api/ (Toda a pasta da API Flask)✅ 3. Implementação (Colocar os Novos Componentes)[ ] Crie/Substitua os Ficheiros:Substitua o conteúdo de core/tools/data_tools.py pelo código do Ficheiro 1.Crie o novo ficheiro core/agents/bi_agent_nodes.py com o conteúdo do Ficheiro 2.Substitua o conteúdo de core/graph/graph_builder.py pelo código do Ficheiro 3.Substitua o conteúdo de main.py na raiz do projeto pelo código do Ficheiro 4.Substitua o conteúdo de streamlit_app.py na raiz do projeto pelo código do Ficheiro 5.✅ 4. Configuração Final[ ] Verifique as Dependências: Abra o seu ficheiro requirements.txt e garanta que as seguintes bibliotecas estão listadas. Se não estiverem, adicione-as:fastapi
uvicorn[standard]
langchain
langchain-openai
langgraph
pydantic-settings
requests
streamlit
plotly
[ ] Instale as Dependências: Execute no seu terminal:pip install -r requirements.txt
[ ] Verifique o .env: Confirme que o seu ficheiro .env na raiz do projeto contém as variáveis necessárias, especialmente OPENAI_API_KEY e SQL_SERVER_CONNECTION_STRING.✅ 5. Execução e Verificação[ ] Terminal 1 (Backend): Inicie o servidor FastAPI.uvicorn main:app --reload
Verifique se não há erros e se ele está a correr em http://127.0.0.1:8000.[ ] Terminal 2 (Frontend): Inicie a interface Streamlit.streamlit run streamlit_app.py
