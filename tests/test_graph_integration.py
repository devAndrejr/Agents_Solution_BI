# tests/test_graph_integration.py
import pytest
from unittest.mock import MagicMock, patch
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage

from core.graph.graph_builder import GraphBuilder
from core.agent_state import AgentState

from core.connectivity.parquet_adapter import ParquetAdapter # Import ParquetAdapter

@pytest.fixture
def mock_adapters():
    """Fixture to create mock adapters for testing."""
    mock_llm_adapter = MagicMock()
    mock_parquet_adapter = MagicMock(spec=ParquetAdapter)
    mock_code_gen_agent = MagicMock()
    return mock_llm_adapter, mock_parquet_adapter, mock_code_gen_agent

def test_graph_builds_and_compiles(mock_adapters):
    """
    Testa se o grafo é construído e compilado sem erros.
    """
    mock_llm_adapter, mock_parquet_adapter, mock_code_gen_agent = mock_adapters
    
    builder = GraphBuilder(
        llm_adapter=mock_llm_adapter,
        parquet_adapter=mock_parquet_adapter,
        code_gen_agent=mock_code_gen_agent
    )
    
    app = builder.build()
    
    assert app is not None
    assert hasattr(app, "invoke")

@patch('core.agents.bi_agent_nodes.fetch_data_from_query')
def test_full_graph_flow_simple_query(mock_fetch_data_tool, mock_adapters):
    """
    Testa um fluxo completo do grafo para uma consulta simples.
    """
    mock_llm_adapter, mock_parquet_adapter, mock_code_gen_agent = mock_adapters

    # --- Mocking Setup ---
    # 1. classify_intent returns 'consulta_sql_complexa'
    mock_llm_adapter.get_completion.side_effect = [
        {
            "content": '{"intent": "consulta_sql_complexa", "entities": {}}'
        },
        # 2. generate_sql_query returns a SQL query
        {
            "content": '{"coluna": "valor"}' # Valid JSON for parquet_filters
        }
    ]
    # 3. get_schema returns a schema
    mock_parquet_adapter.get_schema.return_value = {"tables": ["ADMAT"]}
    # 4. fetch_data_from_query (the tool) returns mock data
    mock_fetch_data_tool.invoke.return_value = [{"product": "A", "price": 100}]

    # --- Graph Execution ---
    builder = GraphBuilder(
        llm_adapter=mock_llm_adapter,
        parquet_adapter=mock_parquet_adapter,
        code_gen_agent=mock_code_gen_agent
    )
    app = builder.build()

    initial_state: AgentState = {
        "messages": [HumanMessage(content="me dê os dados")] # Use HumanMessage
    }
    
    final_state = app.invoke(initial_state)

    # --- Assertions ---
    # Check if the flow went through the correct nodes
    assert mock_llm_adapter.get_completion.call_count == 2
    mock_parquet_adapter.get_schema.assert_called_once()
    mock_fetch_data_tool.invoke.assert_called_once()
    
    # Check the final response
    final_response = final_state.get("final_response")
    assert final_response is not None
    assert final_response["type"] == "data"
    assert final_response["content"][0]["product"] == "A"

@patch('core.agents.bi_agent_nodes.fetch_data_from_query')
def test_full_graph_flow_chart_generation(mock_fetch_data_tool, mock_adapters):
    """
    Testa um fluxo completo do grafo para geração de gráfico.
    """
    mock_llm_adapter, mock_parquet_adapter, mock_code_gen_agent = mock_adapters

    # --- Mocking Setup ---
    # 1. classify_intent returns 'gerar_grafico'
    mock_llm_adapter.get_completion.side_effect = [
        {
            "content": '{"intent": "gerar_grafico", "entities": {"product_id": "369947"}}'
        },
        {
            "content": '{"coluna": "valor"}' # Valid JSON for parquet_filters
        },
        {
            "content": "import pandas as pd\nimport plotly.express as px\ndf_raw_data = pd.DataFrame([{\"MES_01\": 100, \"MES_02\": 150, \"MES_03\": 120}])\nfig = px.bar(df_raw_data.melt(), x=\"variable\", y=\"value\", title=\"Vendas do Produto 369947\")\nresult = fig"
        }
    ]
    # 2. get_schema returns a schema
    mock_parquet_adapter.get_schema.return_value = {"tables": ["ADMAT"], "columns": {"product": "str", "sales": "int"}}
    # 3. fetch_data_from_query (the tool) returns mock data
    mock_fetch_data_tool.invoke.return_value = [{"product": "A", "sales": 100}, {"product": "B", "sales": 200}]
    # 4. code_gen_agent.generate_and_execute_code returns a mock Plotly JSON
    mock_code_gen_agent.generate_and_execute_code.return_value = {
        "type": "chart",
        "output": '''{
            "data": [{"x": ["MES_01", "MES_02", "MES_03"], "y": [100, 150, 120], "type": "bar"}],
            "layout": {
                "title": "Vendas do Produto 369947",
                "xaxis": {"title": "Mês"},
                "yaxis": {"title": "Vendas"}
            }
        }'''
    }

    # --- Graph Execution ---
    builder = GraphBuilder(
        llm_adapter=mock_llm_adapter,
        parquet_adapter=mock_parquet_adapter,
        code_gen_agent=mock_code_gen_agent
    )
    app = builder.build()

    initial_state: AgentState = {
        "messages": [HumanMessage(content="gere um gráfico do produto 369947")]
    }
    
    final_state = app.invoke(initial_state)

    # --- Assertions ---
    mock_parquet_adapter.get_schema.assert_called_once()
    mock_fetch_data_tool.invoke.assert_called_once()
    mock_code_gen_agent.generate_and_execute_code.assert_called_once()
    
    # Check the final response type
    final_response = final_state.get("final_response")
    assert final_response is not None
    assert final_response["type"] == "chart"
    
    # Check the content of the Plotly spec
    chart_content = final_response["content"]
    assert "data" in chart_content
    assert "layout" in chart_content
    assert chart_content["layout"]["title"] == "Vendas do Produto 369947"
    assert "xaxis" in chart_content["layout"]
    assert chart_content["layout"]["xaxis"]["title"] == "Mês"
    assert "yaxis" in chart_content["layout"]
    assert chart_content["layout"]["yaxis"]["title"] == "Vendas"
    assert len(chart_content["data"]) > 0
    assert chart_content["data"][0]["type"] == "bar"
    assert "x" in chart_content["data"][0]
    assert "y" in chart_content["data"][0]
    assert "layout" in final_response["content"]
    assert final_response["content"]["layout"]["title"] == "Vendas do Produto 369947"