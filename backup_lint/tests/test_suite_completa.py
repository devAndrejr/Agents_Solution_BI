# tests/test_suite_completa.py

# Importando a classe base para o mock
from core.llm_base import BaseLLMAdapter
from core.llm_adapter import OpenAILLMAdapter
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, ToolCall
from core.agents.tool_agent import ToolAgent
from core.agents.code_gen_agent import CodeGenAgent
from core.agent_state import AgentState
from core.graph.graph_builder import GraphBuilder
from core.connectivity.sql_server_adapter import SQLServerAdapter
import os
import sys
import pytest
import pyodbc
import unicodedata
from pathlib import Path
from unittest.mock import patch, MagicMock
import plotly.graph_objects as go
import plotly.io as pio


from core.config.settings import settings # Mover para depois do load_dotenv


# --- FUNÇÕES AUXILIARES ---
def normalize_string(s: str) -> str:
    """Remove acentos, caracteres especiais e converte para minúsculas."""
    if not isinstance(s, str):
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn').lower()

# =============================================================================
# FIXTURES - O CORAÇÃO DA SUITE DE TESTES AVANÇADA
# =============================================================================


@pytest.fixture(scope="module")
def db_connection():
    """Fixture para criar e gerenciar uma conexão real com o banco de dados."""
    print("\n[Fixture] Criando conexão com o SQL Server...")
    try:
        db_driver = os.getenv("DB_DRIVER")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_trust = os.getenv("DB_TRUST_SERVER_CERTIFICATE")

        conn_str = (
            f"DRIVER={db_driver};"
            f"SERVER={db_host},{db_port};"
            f"DATABASE={db_name};"
            f"UID={db_user};"
            f"PWD={db_password};"
            f"TrustServerCertificate={db_trust};"
        )
        cnxn = pyodbc.connect(conn_str)
        print("[Fixture] Conexão com SQL Server bem-sucedida!")
        yield cnxn
    except Exception as e:
        pytest.fail(f"Erro fatal na conexão com SQL Server: {e}")
    finally:
        if 'cnxn' in locals() and cnxn:
            cnxn.close()
            print("\n[Fixture] Conexão com SQL Server fechada.")



@pytest.fixture(autouse=True, scope="module")
def mock_llm_adapter():
    """Fixture para criar uma instância mockada do adaptador LLM."""
    mock_llm = MagicMock(spec=OpenAILLMAdapter)
    
    def mock_get_completion(messages, tools=None):
        last_message = messages[-1] if messages else None
        last_message_content = ""
        if isinstance(last_message, dict):
            last_message_content = last_message.get("content", "")
        elif hasattr(last_message, "content"):
            last_message_content = last_message.content

        # Mock response for ToolAgent's "O que você pode fazer?" query
        if "O que você pode fazer?" in last_message_content:
            return {"content": "Eu posso buscar dados de produtos, verificar estoque, listar categorias de produtos e obter a data da última venda de um produto."}
        
        # Mock response for CodeGenAgent's code generation for "Quanto é 10 vezes 2?"
        if "Quanto é 10 vezes 2?" in last_message_content:
            return {"content": "```python\nresult = 10 * 2\n```"}

        # Mock response for CodeGenAgent's code generation for "Mostre um gráfico de vendas para o produto 610403"
        if "Mostre um gráfico de vendas para o produto 610403" in last_message_content:
            fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[1, 3, 2])])
            return {"content": pio.to_json(fig)}
        
        # Default mock response
        return {"content": "Mocked LLM response."}

    mock_llm.get_completion.side_effect = mock_get_completion
    return mock_llm


@pytest.fixture(autouse=True, scope="module")
def patch_openai_llm_adapter(mock_llm_adapter):
    with patch('core.llm_adapter.OpenAILLMAdapter', return_value=mock_llm_adapter):
        yield


@pytest.fixture(autouse=True, scope="module")
def patch_chat_openai():
    with patch('langchain_openai.ChatOpenAI') as MockChatOpenAI:
        mock_chat_openai_instance = MockChatOpenAI.return_value
        
        def mock_invoke(input_data):
            query = input_data["query"]
            if "gráfico" in query:
                # Simulate AIMessage with tool_calls
                return MagicMock(tool_calls=[MagicMock(id="mock_id", name="generate_and_execute_python_code", args={"query": query})])
            elif "colunas" in query:
                return MagicMock(tool_calls=[MagicMock(id="mock_id", name="list_table_columns", args={"table_name": "ADMAT_REBUILT"})])
            else:
                return MagicMock(tool_calls=[MagicMock(id="mock_id", name="query_product_data", args={"query": query})])

        mock_chat_openai_instance.invoke.side_effect = mock_invoke
        yield


@pytest.fixture(scope="module")
def full_graph_app(db_connection, mock_llm_adapter):
    """Fixture que monta e compila o grafo completo com componentes reais."""
    print("[Fixture] Montando o grafo de aplicação completo...")
    db_adapter = SQLServerAdapter(settings)
    code_gen_agent = CodeGenAgent(llm_adapter=mock_llm_adapter)
    graph_builder = GraphBuilder(settings, db_adapter, code_gen_agent, mock_llm_adapter) # Pass mock_llm_adapter
    return graph_builder.build()

# =============================================================================
# CLASSES DE TESTE - ORGANIZANDO OS TESTES
# =============================================================================


@pytest.mark.integration
class TestSetupAndConnectivity:
    def test_sql_server_connection(self, db_connection):
        assert db_connection is not None
        cursor = db_connection.cursor()
        cursor.execute("SELECT 1")
        row = cursor.fetchone()
        assert row[0] == 1, "A consulta de verificação 'SELECT 1' falhou."


@pytest.mark.unit
class TestCodeGenAgentUnit:
    def test_executes_code_successfully(self, mock_llm_adapter):
        mock_llm_adapter.get_completion.return_value = {
            "content": "```python\nresult = 10 * 2\n```"}
        agent = CodeGenAgent(llm_adapter=mock_llm_adapter)
        result = agent.generate_and_execute_code("Quanto é 10 vezes 2?")
        mock_llm_adapter.get_completion.assert_called_once()
        assert result["type"] == "text"
        assert result["output"] == "20"

    def test_handles_no_code_generated(self, mock_llm_adapter):
        mock_llm_adapter.get_completion.return_value = {
            "content": "Desculpe, não sei."}
        agent = CodeGenAgent(llm_adapter=mock_llm_adapter)
        result = agent.generate_and_execute_code("Consulta inválida")
        assert result["type"] == "text"
        assert "Não consegui gerar um script" in result["output"]


@pytest.mark.integration
class TestToolAgentIntegration:
    def test_process_query_describes_tools(self, mock_llm_adapter):
        agent = ToolAgent(llm_adapter=mock_llm_adapter)
        query = "O que você pode fazer?"
        response = agent.process_query(query)
        assert response is not None
        assert response["type"] == "text"
        normalized_output = normalize_string(response["output"])
        print(f"\nSaída Normalizada do ToolAgent: {normalized_output}")
        assert "buscar dados de produtos" in normalized_output
        assert "verificar estoque" in normalized_output
        assert "listar categorias de produtos" in normalized_output
        assert "obter a data da ultima venda de um produto" in normalized_output


@pytest.mark.integration
class TestFullGraphIntegration:
    def test_query_for_table_schema(self, full_graph_app):
        query = 'Liste as colunas da tabela ADMAT_REBUILT.'

    def test_query_for_chart_generation(self, full_graph_app):
        query = "Mostre um gráfico de vendas para o produto 610403"
        initial_state: AgentState = {"messages": [HumanMessage(content=query)]}
        final_state = full_graph_app.invoke(initial_state)
        
        # Verify that the final state contains a plotly figure in additional_kwargs
        assert final_state["messages"][-1].additional_kwargs.get("plotly_fig") is not None, "A mensagem final não contém uma figura Plotly nos additional_kwargs."
        
        # Verify that the figure is a valid Plotly Figure object
        import plotly.graph_objects as go
        assert isinstance(final_state["messages"][-1].additional_kwargs["plotly_fig"], go.Figure), "A figura nos additional_kwargs não é um objeto go.Figure válido."