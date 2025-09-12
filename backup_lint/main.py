'''
API Gateway (Backend) para o Agent_BI usando FastAPI.
Este arquivo substitui a lógica anterior e serve como o ponto de entrada
principal para todas as interações do frontend.
'''
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
    '''
    Endpoint principal que recebe a consulta do usuário, invoca o grafo
    e retorna a resposta final.
    '''
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