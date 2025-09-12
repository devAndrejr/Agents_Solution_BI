import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.query_processor import QueryProcessor
from core.llm_adapter import OpenAILLMAdapter # Import the real LLM adapter
from core.agents.supervisor_agent import SupervisorAgent # Import the real SupervisorAgent

@pytest.fixture
def mock_llm_adapter():
    """Fixture que cria um LLM Adapter mockado."""
    with patch('core.llm_adapter.OpenAILLMAdapter') as MockLLMAdapter:
        mock = MockLLMAdapter.return_value
        yield mock

@pytest.fixture
def query_processor(mock_llm_adapter):
    """Cria uma instância do QueryProcessor para os testes com um SupervisorAgent mockado."""
    # Mock the SupervisorAgent
    with patch('core.query_processor.SupervisorAgent') as MockSupervisorAgent:
        mock_supervisor = MockSupervisorAgent.return_value
        
        # Configure mock_supervisor.route_query based on the query
        def mock_route_query(query):
            if "gráfico" in query:
                # Simulate a chart response
                return {"type": "chart", "output": "mock_chart_data"}
            elif "preço" in query:
                # Simulate a text response
                return {"type": "text", "output": "O preço do produto 719445 é R$ 100,00."}
            else:
                return {"type": "text", "output": "Resposta padrão mockada."}

        mock_supervisor.route_query.side_effect = mock_route_query
        
        # Create QueryProcessor with the mocked SupervisorAgent
        # We need to patch the SupervisorAgent during QueryProcessor initialization
        # This requires a more direct patch on the class itself
        processor = QueryProcessor()
        processor.supervisor = mock_supervisor # Inject the mocked supervisor
        return processor

def test_query_brinquedos_chart(query_processor):
    """Testa uma consulta que deve gerar um gráfico."""
    query = 'mostre um gráfico de vendas por categoria'
    print(f"Executando teste com a consulta: {query}")
    response = query_processor.process_query(query)
    print(f"Resposta recebida: {response}")
    assert response is not None, "A resposta não pode ser nula"
    assert response.get("type") != "error", f"A consulta retornou um erro: {response.get('output')}"
    assert response.get("type") == "chart", "A resposta deve ser do tipo gráfico"

def test_query_price_text(query_processor):
    """Testa uma consulta que deve gerar uma resposta de texto."""
    query = 'qual o preço do produto 719445?'
    print(f"Executando teste com a consulta: {query}")
    response = query_processor.process_query(query)
    print(f"Resposta recebida: {response}")
    assert response is not None, "A resposta não pode ser nula"
    assert response.get("type") != "error", f"A consulta retornou um erro: {response.get('output')}"
    assert response.get("type") == "text", "A resposta deve ser do tipo texto"

if __name__ == "__main__":
    pytest.main([__file__])