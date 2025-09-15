PROMPT MESTRE: IMPLEMENTAÇÃO DA ARQUITETURA AVANÇADA DO AGENT_BI
1. PERSONA E PAPEL
QUEM VOCÊ É:
Você é um Arquiteto de Software Sênior e Engenheiro de IA, especialista em migrar sistemas de agentes complexos para arquiteturas LangGraph robustas, seguindo o padrão de Máquina de Estados Finitos. A sua missão é refatorar um projeto existente para um estado de excelência técnica, focando em modularidade, eficiência (mínimo de chamadas ao LLM), e desacoplamento total entre backend e frontend.

2. CONTEXTO E OBJETIVO GERAL
A SITUAÇÃO ATUAL:
Estou a finalizar a refatoração do projeto Agent_BI. A base do projeto foi transformada numa arquitetura unificada com langgraph, conforme descrito no relatorio_refatoracao_final.md. No entanto, a implementação desta nova arquitetura ainda apresenta erros de integração, de configuração e de lógica.

MEU OBJETIVO FINAL:
Obter o código-fonte completo e corrigido para os componentes chave da nova arquitetura. O sistema final deve ser totalmente funcional, com todas as importações corretas, a configuração devidamente injetada e a lógica dos agentes a operar como esperado dentro do StateGraph.

3. TAREFA ESPECÍFICA E IMEDIATA
SUA TAREFA AGORA:
Com base no relatorio_refatoracao_final.md e no código-fonte atual que fornecerei, analise e reescreva os seguintes cinco (5) ficheiros Python. O objetivo é corrigir todos os erros de inicialização (TypeError, AttributeError), erros de importação (ImportError) e garantir que a lógica implementada corresponde à arquitetura de Máquina de Estados Finitos descrita.

1. core/config/settings.py (Fundação da Configuração):

Reescreva este ficheiro para carregar todas as variáveis de ambiente necessárias (DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD, OPENAI_API_KEY, etc.) a partir de um único ficheiro .env.

Implemente um campo @computed_field chamado SQL_SERVER_CONNECTION_STRING que constrói a string de conexão do SQL Server de forma segura e automática.

2. core/connectivity/sql_server_adapter.py (Conexão Robusta):

Refatore o método __init__ da classe SQLServerAdapter para que ele receba a instância completa de settings (def __init__(self, settings: Settings):), em vez de uma connection_string. Ele deve usar o settings.SQL_SERVER_CONNECTION_STRING internamente para se conectar.

3. core/agents/bi_agent_nodes.py (Lógica dos Estados):

Reveja todas as funções (nós) e garanta que elas interagem corretamente com os outros componentes.

Assegure que a função execute_query chama corretamente a ferramenta fetch_data_from_query e que o seu nome está consistente em todo o sistema.

4. core/graph/graph_builder.py (O Cérebro da Orquestração):

Verifique e corrija todas as importações de bi_agent_nodes.py, garantindo que os nomes das funções correspondem.

Assegure que, ao adicionar os nós ao StateGraph, você está a passar as dependências corretas (como db_adapter) usando functools.partial.

5. main.py (O Ponto de Entrada da API):

Reescreva a função de startup_event para que ela instancie todos os componentes na ordem correta, passando o objeto settings para os adaptadores, conforme as novas assinaturas __init__.

Garanta que o GraphBuilder é instanciado com os adaptadores já prontos e que o grafo é compilado com sucesso.

4. DOCUMENTOS E CÓDIGO-FONTE PARA ANÁLISE
[DOCUMENTO 1: RELATÓRIO DA REFATORAÇÃO FINAL]

### **Relatório Final de Refatoração e Unificação de Arquitetura**

**Objetivo:** Unificar a arquitetura do projeto em torno de uma solução moderna com `langgraph`, eliminando componentes redundantes e aplicando as melhores práticas de design de software, como injeção de dependência.

**Resumo das Etapas Concluídas:**

#### 1. Resolução de Blocker e Criação de Agente Substituto
*   **Problema Identificado:** A refatoração foi inicialmente bloqueada pela ausência do arquivo crítico `core/agents/caculinha_bi_agent.py`, do qual o `graph_builder.py` dependia.
*   **Ação Tomada:** Para contornar o problema e viabilizar a continuidade da refatoração, foi criado um novo arquivo `core/agents/caculinha_bi_agent.py`.
*   **Resultado:** Este arquivo contém um agente de BI substituto (placeholder) funcional, que é capaz de executar consultas SQL através da nova camada de conectividade (`DatabaseAdapter`), permitindo que a arquitetura do grafo seja construída e testada.

#### 2. Centralização da Configuração e Conectividade
*   **Configuração:** A biblioteca `pydantic-settings` foi adicionada e o módulo `core/config/settings.py` foi criado para centralizar todas as configurações da aplicação.
*   **Conectividade:** A camada de conectividade foi abstraída com a criação do diretório `core/connectivity`, da interface `DatabaseAdapter` e da implementação `SQLServerAdapter`.
*   **Resultado:** As configurações e o acesso ao banco de dados foram desacoplados do resto da aplicação, tornando o sistema mais modular e fácil de manter.

#### 3. Refatoração e Unificação da Arquitetura `LangGraph`
*   **Injeção de Dependência:** O arquivo `core/graph/graph_builder.py` foi completamente refatorado. Agora, a classe `GraphBuilder` recebe as instâncias de `Settings` e `DatabaseAdapter` em seu construtor.
*   **Integração do Novo Agente:** O grafo agora utiliza o novo agente de BI substituto, injetando o `DatabaseAdapter` para que ele possa interagir com o banco de dados.
*   **Resultado:** O `langgraph` tornou-se o núcleo de orquestração definitivo do projeto, com suas dependências explicitamente injetadas, seguindo as melhores práticas de design.

#### 4. Atualização dos Pontos de Entrada e Scripts
*   **Interface do Usuário (`streamlit_app.py`):** A aplicação Streamlit foi refatorada para instanciar e usar o novo `GraphBuilder`, abandonando o antigo `QueryProcessor`.
*   **API (`core/main.py` e `chat_routes.py`):** Os endpoints da API (FastAPI e Flask) que processavam consultas foram atualizados para usar a nova arquitetura unificada com `langgraph`.
*   **Scripts e Testes:** O script de avaliação (`scripts/evaluate_agent.py`) e os testes de integração (`tests/test_real_queries.py`) foram reescritos para serem compatíveis com o novo sistema.
*   **Resultado:** Todos os pontos de interação do usuário e sistemas de teste agora utilizam a mesma arquitetura central, garantindo consistência e comportamento unificado.

#### 5. Remoção de Componentes Redundantes
*   **Ação de Limpeza:** Os seguintes arquivos, que representavam a arquitetura antiga e conflitante, foram removidos com segurança do projeto:
    *   `core/query_processor.py`
    *   `core/agents/supervisor_agent.py`
    *   `tests/test_supervisor_agent.py`
*   **Resultado:** O código-fonte foi significativamente limpo, eliminando a confusão e a redundância, e deixando apenas uma arquitetura coesa e clara.

---

**Conclusão Final:**

O projeto "Agent BI" foi transformado com sucesso, passando de uma arquitetura com componentes duplicados e acoplados para um sistema unificado, robusto e moderno, centrado no `langgraph` e em padrões de design avançados. A base de código está agora mais limpa, mais fácil de manter e pronta para futuras expansões.
[CÓDIGO-FONTE ATUAL PARA CORREÇÃO]
(INSTRUÇÃO: COLE AQUI O CÓDIGO DOS SEUS FICHEIROS ATUAIS QUE ESTÃO A CAUSAR ERROS)

Ficheiro 1: core/config/settings.py

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import urllib

class Settings(BaseSettings):
    """
    Centraliza as configurações da aplicação, carregando variáveis de um ficheiro .env.
    Esta versão foi refatorada para ser mais robusta, construindo a connection string
    diretamente a partir das variáveis de ambiente.
    """
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8',
        extra='ignore' # Ignora variáveis extras no .env
    )

    # Variáveis de ambiente individuais para a base de dados
    DB_SERVER: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_DRIVER: str = "{ODBC Driver 17 for SQL Server}" # Valor padrão comum

    # Chave da API para o LLM
    OPENAI_API_KEY: SecretStr
    
    # Campo Computado: Constrói a connection string dinamicamente
    @computed_field
    @property
    def SQL_SERVER_CONNECTION_STRING(self) -> str:
        """
        Gera a string de conexão ODBC para o SQL Server de forma segura.
        """
        driver_formatted = self.DB_DRIVER.replace(' ', '+')
        password_quoted = urllib.parse.quote_plus(self.DB_PASSWORD.get_secret_value())
        
        return (
            f"mssql+pyodbc://{self.DB_USER}:{password_quoted}@"
            f"{self.DB_SERVER}/{self.DB_NAME}?"
            f"driver={driver_formatted}"
        )

# Instância única das configurações para ser usada em toda a aplicação
settings = Settings()
Ficheiro 2: core/connectivity/sql_server_adapter.py

# core/connectivity/sql_server_adapter.py
from typing import Any, Dict, List
import pyodbc
from .base import DatabaseAdapter
from core.config.settings import Settings # Importa a nova classe de config

class SQLServerAdapter(DatabaseAdapter):
    """Concrete implementation of the adapter for Microsoft SQL Server."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._connection = None
        self._cursor = None

    def connect(self) -> None:
        """Establishes connection using the centralized settings."""
        if not self._connection:
            try:
                self._connection = pyodbc.connect(self._settings.PYODBC_CONNECTION_STRING)
                self._cursor = self._connection.cursor()
                print("SQL Server connection successful.")
            except pyodbc.Error as ex:
                sqlstate = ex.args[0]
                print(f"SQL Server connection failed: {sqlstate}")
                raise

    def disconnect(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None
            print("SQL Server connection closed.")

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        if not self._cursor:
            self.connect()
        
        self._cursor.execute(query)
        columns = [column[0] for column in self._cursor.description]
        results = [dict(zip(columns, row)) for row in self._cursor.fetchall()]
        return results

    def get_schema(self) -> Dict[str, Any]:
        self.connect() # Ensure connection is established
        # Lógica para inspecionar o schema do banco de dados
        # (Exemplo simplificado)
        self._cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in self._cursor.fetchall()]
        return {"tables": tables}
Ficheiro 3: core/agents/bi_agent_nodes.py

"""
Nós (estados) para o StateGraph da arquitetura avançada do Agent_BI.
Cada função representa um passo no fluxo de processamento da consulta.
"""
import logging
import json
from typing import Dict, Any
import pandas as pd

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
    user_query = state['messages'][-1].content
    
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
    user_query = state['messages'][-1].content
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
        return {"final_response": {"type": "text", "content": "Não foi possível obter dados para gerar o gráfico."}}

    try:
        if not raw_data: return {"final_response": {"type": "text", "content": "A consulta não retornou dados para visualização."}}
        
        df = pd.DataFrame(raw_data)
        keys = list(df.columns)
        dimension, metric = keys[0], keys[1]
        
        plotly_spec = {
            "data": [{"x": df[dimension].tolist(), "y": df[metric].tolist(), "type": "bar"}],
            "layout": {"title": f"{str(metric).title()} por {str(dimension).title()}"}
        }
        return {"plotly_spec": plotly_spec}
    except Exception as e:
        logger.error(f"Erro ao gerar especificação Plotly: {e}")
        return {"final_response": {"type": "text", "content": f"Não consegui gerar o gráfico."}}

def format_final_response(state: AgentState) -> Dict[str, Any]:
    """
    Formata a resposta final para o utilizador.
    """
    logger.info("Nó: format_final_response")
    response = {}
    if state.get("clarification_needed"):
        response = {"type": "clarification", "content": state.get("clarification_options")}
    elif state.get("plotly_spec"):
        response = {"type": "chart", "content": state.get("plotly_spec")}
    elif state.get("raw_data"):
        response = {"type": "data", "content": state.get("raw_data")}
    else:
        response = {"type": "text", "content": "Não consegui processar a sua solicitação."}
        
    final_messages = state['messages'] + [{"role": "assistant", "content": response}]
    return {"messages": final_messages, "final_response": response}
Ficheiro 4: core/graph/graph_builder.py

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
from core.connectivity.base import DatabaseAdapter
from core.agents.code_gen_agent import CodeGenAgent
# CORREÇÃO: Removida a importação da função inexistente.
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
        self.llm_adapter = ll_adapter
        self.db_adapter = db_adapter
        self.code_gen_agent = code_gen_agent

    def _decide_after_intent_classification(self, state: AgentState) -> str:
        """
        Aresta condicional que roteia o fluxo após a classificação da intenção.
        """
        intent = state.get("intent")
        logger.info(f"Roteando com base na intenção: {intent}")
        if intent == "gerar_grafico":
            return "clarify_requirements"
        elif intent == "consulta_sql_complexa":
            return "generate_sql_query"
        else: # resposta_simples ou fallback
            return "generate_sql_query"

    def _decide_after_clarification(self, state: AgentState) -> str:
        """
        Aresta condicional que decide o fluxo após a verificação de requisitos.
        """
        if state.get("clarification_needed"):
            logger.info("Esclarecimento necessário. Finalizando para obter input do usuário.")
            return "format_final_response"
        else:
            logger.info("Nenhum esclarecimento necessário. Prosseguindo para gerar SQL.")
            return "generate_sql_query"

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
        generate_sql_query_node = partial(bi_agent_nodes.generate_sql_query, code_gen_agent=self.code_gen_agent)
        # CORREÇÃO: A função correta 'execute_query' de bi_agent_nodes é usada aqui.
        execute_query_node = partial(bi_agent_nodes.execute_query, db_adapter=self.db_adapter)

        # Adiciona os nós (estados) ao grafo
        workflow.add_node("classify_intent", classify_intent_node)
        workflow.add_node("clarify_requirements", bi_agent_nodes.clarify_requirements)
        workflow.add_node("generate_sql_query", generate_sql_query_node)
        # CORREÇÃO: O nó é adicionado com o nome correto, correspondendo à função.
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
        workflow.add_conditional_edge(
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
Ficheiro 5: main.py

"""
API Gateway (Backend) para o Agent_BI usando FastAPI.
"""
import uvicorn
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage

# Importações dos componentes da nova arquitetura
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
    session_id: str = Field(..., description="ID de sessão para gerenciar o estado da conversa")

# --- Inicialização da Aplicação ---
app = FastAPI(
    title="Agent_BI - API Gateway",
    description="Backend FastAPI para a nova arquitetura com LangGraph.",
    version="3.0.0"
)

@app.on_event("startup")
def startup_event():
    """Inicializa as dependências na inicialização da aplicação."""
    logger.info("Inicializando dependências...")
    app.state.llm_adapter = OpenAILLMAdapter(api_key=settings.OPENAI_API_KEY.get_secret_value())
    app.state.db_adapter = SQLServerAdapter(connection_string=settings.SQL_SERVER_CONNECTION_STRING)
    app.state.code_gen_agent = CodeGenAgent(llm_adapter=app.state.llm_adapter)
    graph_builder = GraphBuilder(
        llm_adapter=app.state.llm_adapter,
        db_adapter=app.state.db_adapter,
        code_gen_agent=app.state.code_gen_agent
    )
    app.state.agent_graph = graph_builder.build()
    logger.info("Dependências e grafo inicializados com sucesso.")

# --- Endpoints da API ---
@app.post("/api/v1/query")
async def handle_query(request: QueryRequest):
    """
    Endpoint principal que recebe a consulta do utilizador, invoca o grafo
    e retorna a resposta final.
    """
    logger.info(f"Recebida nova query para session_id='{request.session_id}': '{request.user_query}'")
    try:
        initial_state = {"messages": [HumanMessage(content=request.user_query)]}
        final_state = app.state.agent_graph.invoke(initial_state)
        response_content = final_state.get("final_response", {})
        return response_content
    except Exception as e:
        logger.error(f"Erro crítico ao invocar o grafo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno no servidor do agente.")

@app.get("/status")
def status():
    return {"status": "Agent_BI API is running"}

# --- Execução da Aplicação ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)