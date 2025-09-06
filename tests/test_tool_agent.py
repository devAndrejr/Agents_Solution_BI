# tests/test_tool_agent.py
import sys
import os
import pytest
import unicodedata # Adicionado para normalização de strings
# from unittest.mock import patch, MagicMock # Removido, pois não usaremos mocks

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agents.tool_agent import ToolAgent
from core.llm_adapter import OpenAILLMAdapter
from core.llm_langchain_adapter import CustomLangChainLLM

def normalize_string(s):
    # Remove acentos e caracteres especiais, e converte para minúsculas
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn').lower()

@pytest.fixture
def agent():
    """
    Cria uma instância do ToolAgent para os testes, usando um LLM real.
    """
    # Instancia o LLM real
    llm_adapter = OpenAILLMAdapter() # Renomeado para llm_adapter para clareza

    # Não mockamos _create_agent_executor, permitindo que ele crie o executor real
    agent_instance = ToolAgent(llm_adapter=llm_adapter)
    yield agent_instance

def test_tool_agent_process_query(agent):
    """
    Testa se o ToolAgent chama corretamente o seu executor com a consulta do usuário.
    """
    query = "Qual o esquema do banco de dados?"
    response = agent.process_query(query)

    # Verificamos se a resposta do 'process_query' está no formato correto
    assert response is not None
    assert response["type"] == "text"
    
    normalized_output = normalize_string(response["output"])
    
    expected_part1 = normalize_string("o banco de dados e composto por dois arquivos parquet principais")
    expected_part2 = normalize_string("admatao.parquet")
    expected_part3 = normalize_string("vendas.parquet")
    expected_part4 = normalize_string("buscar dados especificos sobre produtos")

    # Verificamos se a resposta contém o texto esperado do ToolAgent
    assert expected_part1 in normalized_output
    assert expected_part2 in normalized_output
    assert expected_part3 in normalized_output
    assert expected_part4 in normalized_output

if __name__ == "__main__":
    pytest.main([__file__])
