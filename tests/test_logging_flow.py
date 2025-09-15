
# tests/test_logging_flow.py
import logging
import os
import sys

# Adiciona o diretório raiz ao path para resolver os imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from core.config.logging_config import setup_logging
from core.graph.graph_builder import GraphBuilder
from core.config.settings import settings
from core.llm_adapter import OpenAILLMAdapter
from core.connectivity.parquet_adapter import ParquetAdapter

from langchain_core.messages import HumanMessage

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)
user_interaction_logger = logging.getLogger("user_interaction")

logger.info("--- Iniciando teste de fluxo de logging ---")

# Build the graph
try:
    logger.info("Construindo o grafo de agentes...")
    llm_adapter = OpenAILLMAdapter(api_key=settings.OPENAI_API_KEY.get_secret_value())
    parquet_adapter = ParquetAdapter(file_path=r"C:\Users\André\Documents\Agent_BI\data\parquet\admatao.parquet") # Corrected path and raw string
    mock_code_gen_agent = lambda: "mock" 

    builder = GraphBuilder(
        llm_adapter=llm_adapter,
        parquet_adapter=parquet_adapter,
        code_gen_agent=mock_code_gen_agent
    )
    app = builder.build()
    logger.info("Grafo construído com sucesso.")
except Exception as e:
    logger.error(f"Falha ao construir o grafo: {e}", exc_info=True)
    exit()

# Invoke the graph
try:
    logger.info("Invocando o grafo com uma consulta de teste.")
    query = "gere um gráfico de vendas de barras do produto 369947?"
    initial_state = {"messages": [HumanMessage(content=query)]}
    
    final_state = app.invoke(initial_state)
    
    response = final_state.get("final_response", {"content": "Nenhuma resposta gerada."})
    
    user_interaction_logger.info(f"User query: '{query}' | Agent response: '{response}'")
    
    logger.info("Grafo invocado com sucesso.")

except Exception as e:
    logger.error(f"Falha ao invocar o grafo: {e}", exc_info=True)

logger.info("--- Teste de fluxo de logging finalizado ---")
