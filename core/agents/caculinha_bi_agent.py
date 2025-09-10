import logging
import re
import json # Added import
import uuid # Added import
from typing import List, Dict, Any, Tuple
import pandas as pd
import os
from langchain_core.tools import tool
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, ToolCall
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from core.llm_langchain_adapter import CustomLangChainLLM

from core.connectivity.base import DatabaseAdapter
from core.config.settings import settings # Import the settings instance

logger = logging.getLogger(__name__)

def create_caculinha_bi_agent(
    parquet_dir: str,
    code_gen_agent: Any, # Use Any for now to avoid circular imports
    llm_adapter: Any # Add llm_adapter for tool selection
) -> Tuple[Runnable, List]:
    """
    Cria um agente de BI substituto e suas ferramentas, com o adaptador de banco de dados injetado.

    Args:
        db_adapter: Uma instância que segue a interface DatabaseAdapter.

    Returns:
        Uma tupla contendo o agente executável e a lista de suas ferramentas.
    """

    from core.tools.data_tools import query_product_data, list_table_columns

    @tool
    def generate_and_execute_python_code(query: str) -> Dict[str, Any]:
        """Gera e executa código Python para análises complexas e gráficos."""
        logger.info(f"Gerando e executando código Python para a consulta: {query}")
        return code_gen_agent.generate_and_execute_code(query)

    # A lista de ferramentas agora é definida dentro do escopo que tem acesso ao db_adapter
    bi_tools = [query_product_data, list_table_columns, generate_and_execute_python_code]

    # --- LLM para Geração de SQL ---
    sql_gen_llm = ChatOpenAI(
        model=settings.LLM_MODEL_NAME,
        openai_api_key=settings.OPENAI_API_KEY.get_secret_value(),
        temperature=0,
    )

    # Get parquet schema
    # This is a simplified way to get schema from parquet.
    # In a real scenario, you might have a metadata store for parquet files.
    parquet_schema = {}
    try:
        df_sample = pd.read_parquet(os.path.join(parquet_dir, "ADMAT_REBUILT.parquet"), columns=[])
        for col in df_sample.columns:
            parquet_schema[col] = str(df_sample[col].dtype)
    except Exception as e:
        logger.error(f"Erro ao inferir esquema do parquet: {e}")
        parquet_schema = {"error": "Não foi possível inferir o esquema do parquet."}
    
    schema_str = "\n".join([f"- {col}: {dtype}" for col, dtype in parquet_schema.items()]) # Convert schema to string for the prompt

    sql_gen_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Você é um assistente de BI. Sua tarefa é converter a consulta em linguagem natural do usuário em um objeto JSON que representa os filtros para consultar o arquivo ADMAT_REBUILT.parquet.
O arquivo está localizado em 'C:/Users/André/Documents/Agent_BI/data/parquet_cleaned/ADMAT_REBUILT.parquet'.

Use o seguinte esquema de dados (coluna: tipo) para gerar os filtros JSON:
{tables}

**IMPORTANTE: Para o código do produto, use a coluna 'CÓDIGO' (com acento e maiúsculas) conforme o schema do Parquet.**

Retorne APENAS o objeto JSON. Não inclua explicações ou qualquer outro texto.
O JSON deve ter a seguinte estrutura:
{{
    "target_file": "ADMAT_REBUILT.parquet",
    "filters": [
        {{"column": "nome_da_coluna", "operator": "operador", "value": "valor"}}
    ]
}}

Operadores suportados: "==", "!=", ">", "<", "contains".
Para buscas em colunas de texto (string), sempre use o operador "contains".
Para buscas em colunas numéricas, use "==", "!=", ">", "<".

Exemplo 1:
Consulta: Qual é o preço do produto 369947?
JSON:
```json
{{
    "target_file": "ADMAT_REBUILT.parquet",
    "filters": [
        {{"column": "CÓDIGO", "operator": "==", "value": 369947}}
    ]
}}
```

Exemplo 2:
Consulta: Liste todos os produtos da categoria 'Eletrônicos' com preço maior que 100.
JSON:
```json
{{
    "target_file": "ADMAT_REBUILT.parquet",
    "filters": [
        {{"column": "categoria", "operator": "contains", "value": "Eletrônicos"}},
        {{"column": "preco_38_percent", "operator": ">", "value": 100}}
    ]
}}
```

Exemplo 3:
Consulta: Mostre os produtos com vendas nos últimos 30 dias maiores que 50.
JSON:
```json
{{
    "target_file": "ADMAT_REBUILT.parquet",
    "filters": [
        {{"column": "VEND# QTD 30D", "operator": ">", "value": 50}}
    ]
}}
```


"""
            ),
            ("user", "{query}")
        ]
    )

    sql_generator_chain = sql_gen_prompt | sql_gen_llm

    def agent_runnable_logic(state: Dict[str, Any]) -> Dict[str, Any]:
        last_message = state["messages"][-1]

        if isinstance(last_message, HumanMessage):
            user_query = last_message.content
            logger.info(f"Agente de BI recebeu a consulta: {user_query}")

            # LLM para decisão de ferramenta
            tool_selection_llm = CustomLangChainLLM(llm_adapter=llm_adapter)

            tool_selection_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "Você é um assistente de BI. Sua tarefa é decidir qual ferramenta usar para responder à consulta do usuário. As ferramentas disponíveis são:\n" 
                        "- `query_product_data`: Para consultas que podem ser respondidas buscando dados específicos de produtos com filtros (ex: buscar preço de produto, listar produtos por categoria).\n" 
                        "- `list_table_columns`: Para listar todas as colunas de uma tabela (arquivo Parquet) específica.\n" 
                        "- `generate_and_execute_python_code`: Para análises complexas, cálculos, agregações ou geração de gráficos que exigem código Python.\n\n" 
                        "Retorne APENAS o nome da ferramenta: `query_product_data`, `list_table_columns` ou `generate_and_execute_python_code`.",
                    ),
                    ("user", "{query}"),
                ]
            )

            tool_selection_chain = tool_selection_prompt | tool_selection_llm
            
            # Decide qual ferramenta usar
            tool_decision_message = tool_selection_chain.invoke({"query": user_query})
            tool_decision = tool_decision_message.content.strip()
            logger.info(f"Decisão da ferramenta: {tool_decision}")

            if "query_product_data" in tool_decision:
                # Gerar JSON de filtros e retornar ToolCall
                generated_json_message = sql_generator_chain.invoke({"query": user_query, "tables": schema_str})
                generated_json_content = generated_json_message.content.strip()
                
                json_match = re.search(r"```json\n(.*?)```", generated_json_content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                else:
                    json_str = generated_json_content
                
                try:
                    parsed_json = json.loads(json_str)
                    target_file = parsed_json.get("target_file", "ADMAT_REBUILT.parquet")
                    filters = parsed_json.get("filters", [])
                    logger.info(f"JSON de filtros gerado: {parsed_json}")
                    
                    # Return AIMessage encapsulating ToolCall for query_product_data
                    return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="query_product_data", args={"target_file": target_file, "filters": filters})])]}
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON gerado: {e}. Conteúdo: {json_str}")
                    return {"messages": state["messages"] + [AIMessage(content=f"Desculpe, não consegui processar sua consulta devido a um erro na geração dos filtros: {e}")]}

            elif "list_table_columns" in tool_decision:
                table_name = "ADMAT_REBUILT" # This needs to be dynamically extracted in a real scenario
                logger.info(f"Listando colunas para a tabela: {table_name}")
                # Return AIMessage encapsulating ToolCall for list_table_columns
                return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="list_table_columns", args={"table_name": table_name})])]}

            elif "generate_and_execute_python_code" in tool_decision:
                # Return AIMessage encapsulating ToolCall for CodeGenAgent
                return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="generate_and_execute_python_code", args={"query": user_query})])]}
            else:
                return {"messages": [AIMessage(content="Desculpe, não consegui determinar a ferramenta apropriada para sua consulta.")]}

        elif isinstance(last_message, ToolMessage):
            # This path is taken after a tool has been executed by the ToolNode.
            # The agent needs to process the tool's output and generate an AIMessage.
            # The AIMessage generation is now handled by process_bi_tool_output_func in graph_builder.py
            return state
        else:
            # Handle other unexpected message types
            formatted_output = f"Erro: Tipo de mensagem inesperado no estado: {type(last_message)}"
            logger.error(formatted_output)
            return {"messages": state["messages"] + [AIMessage(content=formatted_output)]}

    # O runnable é a própria lógica do agente
    agent_runnable = RunnableLambda(agent_runnable_logic)

    return agent_runnable, bi_tools

