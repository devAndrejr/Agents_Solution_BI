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
from core.config.logging_config import setup_logging
from core.llm_adapter import OpenAILLMAdapter
from core.connectivity.parquet_adapter import ParquetAdapter # CORRECTED IMPORT
from core.agents.code_gen_agent import CodeGenAgent

# Configuração de logging
setup_logging()
logger = logging.getLogger(__name__)
interaction_logger = logging.getLogger("user_interaction")

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
    app.state.parquet_adapter = ParquetAdapter(file_path="C:\\Users\\André\\Documents\\Agent_BI\\data\\parquet\\admatao.parquet") # CORRECTED INSTANTIATION
    app.state.code_gen_agent = CodeGenAgent(llm_adapter=app.state.llm_adapter)
    graph_builder = GraphBuilder(
        llm_adapter=app.state.llm_adapter,
        parquet_adapter=app.state.parquet_adapter, # CORRECTED PARAMETER NAME
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
    logger.info(f"📝 API REQUEST - Session: {request.session_id} | Query: '{request.user_query}'")
    interaction_logger.info(f"USER_QUERY (session: {request.session_id}): {request.user_query}")

    try:
        initial_state = {"messages": [HumanMessage(content=request.user_query)]}
        logger.info(f"🚀 GRAPH INVOCATION - Starting with state: {initial_state}")

        final_state = app.state.agent_graph.invoke(initial_state)
        response_content = final_state.get("final_response", {})

        # ✅ GARANTIR que a resposta inclui informações da pergunta
        if "user_query" not in response_content:
            response_content["user_query"] = request.user_query

        # 🔍 LOG detalhado da resposta
        logger.info(f"✅ GRAPH SUCCESS - Response type: {response_content.get('type', 'unknown')}")
        logger.info(f"📝 USER QUERY preserved: '{request.user_query}'")
        logger.info(f"📋 FINAL STATE messages count: {len(final_state.get('messages', []))}")
        interaction_logger.info(f"AGENT_RESPONSE (session: {request.session_id}): {response_content}")

        return response_content

    except MemoryError as e:
        error_msg = f"Erro de memória ao processar query: {e}"
        logger.error(f"📥 MEMORY ERROR (session: {request.session_id}): {error_msg}", exc_info=True)
        interaction_logger.error(f"MEMORY_ERROR (session: {request.session_id}): {error_msg}")
        raise HTTPException(status_code=507, detail="Dados muito grandes para processar. Tente usar filtros mais específicos.")

    except Exception as e:
        error_msg = f"Erro crítico ao invocar o grafo: {e}"
        logger.error(f"❌ CRITICAL ERROR (session: {request.session_id}): {error_msg}", exc_info=True)
        interaction_logger.error(f"ERROR (session: {request.session_id}): {error_msg}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor do agente.")

@app.get("/status")
def status():
    return {"status": "Agent_BI API is running"}

# --- Execução da Aplicação ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) # CORRECTED LINE
