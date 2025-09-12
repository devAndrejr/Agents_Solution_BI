# tests/test_supervisor_agent.py
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agents.supervisor_agent import SupervisorAgent

@pytest.fixture
def supervisor():
    """
    Cria uma instância do SupervisorAgent com seus agentes especialistas e LLM mockados.
    """
    # Substituímos as classes dos agentes e do LLM por mocks
    with patch('core.agents.supervisor_agent.ToolAgent') as MockToolAgent, \
         patch('core.agents.supervisor_agent.CodeGenAgent') as MockCodeGenAgent, \
         patch('core.agents.supervisor_agent.BaseLLMAdapter') as MockLLMAdapter:
        
        # Configuramos os mocks dos agentes especialistas
        mock_tool_agent = MockToolAgent.return_value
        mock_tool_agent.process_query.return_value = {"output": "Resposta do ToolAgent"}
        
        mock_code_gen_agent = MockCodeGenAgent.return_value
        mock_code_gen_agent.generate_and_execute_code.return_value = {"output": "Resultado do CodeGenAgent"}

        # Configuramos o mock do LLM de roteamento
        mock_routing_llm = MockLLMAdapter.return_value
        mock_routing_llm.get_completion.return_value = {"content": "tool"} # Valor padrão para evitar erros iniciais

        # Instanciamos o supervisor, que usará todos os mocks
        supervisor_instance = SupervisorAgent(llm_adapter=mock_routing_llm) # Passando o mock do llm_adapter
        # Anexamos os mocks à instância para fácil acesso nos testes
        supervisor_instance.tool_agent = mock_tool_agent
        supervisor_instance.code_gen_agent = mock_code_gen_agent
        # supervisor_instance.routing_llm = mock_routing_llm # Não é mais necessário, pois é passado no construtor
        
        yield supervisor_instance

def test_supervisor_routes_to_tool_agent(supervisor):
    """
    Testa se o supervisor roteia corretamente uma consulta simples para o ToolAgent.
    """
    # Forçamos a decisão de roteamento para "tool"
    supervisor.routing_llm.invoke.return_value.content = "tool"
    
    query = "Qual o preço do produto X?"
    response = supervisor.route_query(query)

    # Verificamos se o ToolAgent foi chamado e se o CodeGenAgent não foi
    supervisor.tool_agent.process_query.assert_called_once_with(query)
    supervisor.code_gen_agent.generate_and_execute_code.assert_not_called()
    
    # Verificamos se a resposta é a que esperamos do ToolAgent
    assert response["output"] == "Resposta do ToolAgent"

def test_supervisor_routes_to_code_gen_agent(supervisor):
    """
    Testa se o supervisor roteia corretamente uma consulta complexa para o CodeGenAgent.
    """
    # Forçamos a decisão de roteamento para "code"
    supervisor.routing_llm.get_completion.return_value = {"content": "code"}
    
    query = "Qual o total de vendas por categoria?"
    response = supervisor.route_query(query)

    # Verificamos se o CodeGenAgent foi chamado e se o ToolAgent não foi
    supervisor.code_gen_agent.generate_and_execute_code.assert_called_once_with(query)
    supervisor.tool_agent.process_query.assert_not_called()

    # Verificamos se a resposta é a que esperamos do CodeGenAgent
    assert response["output"] == "Resultado do CodeGenAgent"

if __name__ == "__main__":
    pytest.main([__file__])
