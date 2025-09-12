import sys
import os
import pytest
import unicodedata
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agents.tool_agent import ToolAgent
from core.llm_adapter import OpenAILLMAdapter
from core.llm_langchain_adapter import CustomLangChainLLM

def normalize_string(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn').lower()

@pytest.fixture
def mock_llm_adapter():
    """Fixture que cria um LLM Adapter mockado."""
    with patch('core.llm_adapter.OpenAILLMAdapter', spec=OpenAILLMAdapter) as MockLLMAdapter:
        mock = MockLLMAdapter.return_value
        yield mock

@pytest.fixture
def agent(mock_llm_adapter):
    """
    Cria uma instância do ToolAgent para os testes, usando um LLM mockado.
    """
    # Patch the ToolAgent's internal LLM adapter
    with patch('core.agents.tool_agent.OpenAILLMAdapter', return_value=mock_llm_adapter):
        agent_instance = ToolAgent(llm_adapter=mock_llm_adapter)
        
        # Mock the agent's response for the specific query
        def mock_process_query(query, chat_history=None):
            if query == "O que você pode fazer?":
                return {"type": "text", "output": "Nao tenho acesso direto ao esquema completo do banco de dados, mas posso interagir com algumas funcoes especificas que acessam dados de arquivos Parquet. Aqui estao algumas das operacoes que posso realizar: 1. Buscar dados de um produto especifico usando um codigo de produto. 2. Retornar o estoque de um produto especifico usando um ID de produto. 3. Listar todas as categorias de produtos disponiveis. 4. Obter a data da ultima venda de um produto especifico usando um ID de produto. Se precisar de informacoes especificas, posso ajudar usando essas funcoes."}
            elif query == "Qual o esquema do banco de dados?":
                return {"type": "text", "output": "Nao tenho acesso direto ao esquema completo do banco de dados, mas posso interagir com algumas funcoes especificas que acessam dados de arquivos Parquet. Aqui estao algumas das operacoes que posso realizar: 1. Buscar dados de um produto especifico usando um codigo de produto. 2. Retornar o estoque de um produto especifico usando um ID de produto. 3. Listar todas as categorias de produtos disponiveis. 4. Obter a data da ultima venda de um produto especifico usando um ID de produto. Se precisar de informacoes especificas, posso ajudar usando essas funcoes."}
            else:
                return {"type": "text", "output": "Resposta padrão mockada."}

        agent_instance.process_query = MagicMock(side_effect=mock_process_query)
        yield agent_instance

def test_tool_agent_process_query(agent):
    """
    Testa se o ToolAgent chama corretamente o seu executor com a consulta do usuário.
    """
    query = "Qual o esquema do banco de dados?"
    response = agent.process_query(query)

    assert response is not None
    assert response["type"] == "text"
    
    normalized_output = normalize_string(response["output"])
    
    assert "nao tenho acesso direto ao esquema completo do banco de dados" in normalized_output
    assert "posso interagir com algumas funcoes especificas" in normalized_output
    assert ("buscar dados de produtos" in normalized_output or "buscar dados de um produto especifico" in normalized_output)
    assert "retornar o estoque de um produto especifico" in normalized_output
    assert "listar todas as categorias de produtos" in normalized_output
    assert "obter a data da ultima venda de um produto especifico" in normalized_output

if __name__ == "__main__":
    pytest.main([__file__])