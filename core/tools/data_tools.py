import json # Added import
from typing import List, Dict, Any, Tuple
import pandas as pd
import os
import logging
from decimal import Decimal # Added import

logger = logging.getLogger(__name__)

# Caminho base para os arquivos Parquet
PARQUET_BASE_PATH = "data/parquet_cleaned"

def list_table_columns(table_name: str) -> str:
    """
    Lista todas as colunas de uma tabela (arquivo Parquet).

    Args:
        table_name (str): O nome da tabela (sem a extensão .parquet).

    Returns:
        str: Uma string JSON contendo a lista de colunas ou uma mensagem de erro.
    """
    file_path = os.path.join(PARQUET_BASE_PATH, f"{table_name}.parquet")
    if not os.path.exists(file_path):
        error_msg = json.dumps({"error": f"Arquivo Parquet não encontrado para a tabela: {table_name}"})
        logger.info(f"list_table_columns returning error: {error_msg}")
        return error_msg

    try:
        df = pd.read_parquet(file_path)
        columns = df.columns.tolist()
        result_json = json.dumps({"columns": columns})
        logger.info(f"list_table_columns returning success: {result_json}")
        return result_json
    except Exception as e:
        error_msg = json.dumps({"error": f"Erro ao ler o arquivo Parquet ou listar colunas: {e}"})
        logger.info(f"list_table_columns returning exception error: {error_msg}")
        return error_msg

def query_product_data(target_file: str, filters: list = None) -> str:
    """
    Consulta dados de um arquivo Parquet com base em filtros.

    Args:
        target_file (str): O nome do arquivo Parquet (ex: 'ADMAT_REBUILT.parquet').
        filters (list): Uma lista de dicionários de filtro. Cada dicionário deve ter 'column', 'operator' e 'value'.
                        Ex: [{'column': 'codigo', 'operator': '==', 'value': 719445}]

    Returns:
        str: Uma string JSON contendo os dados filtrados ou uma mensagem de erro.
    """
    file_path = os.path.join(PARQUET_BASE_PATH, target_file)
    if not os.path.exists(file_path):
        error_msg = json.dumps({"error": f"Arquivo Parquet não encontrado: {target_file}"})
        logger.info(f"query_product_data returning error: {error_msg}")
        return error_msg

    try:
        df = pd.read_parquet(file_path)

        if filters:
            for f in filters:
                column = f.get('column')
                operator = f.get('operator')
                value = f.get('value')

                if not all([column, operator, value is not None]):
                    return json.dumps({"error": "Filtro inválido: 'column', 'operator' e 'value' são obrigatórios."})

                if column not in df.columns:
                    return json.dumps({"error": f"Coluna '{column}' não encontrada no arquivo {target_file}."})

                # Convert value to the correct type if necessary (e.g., for numeric comparisons)
                # This is a simplified approach; a more robust solution might involve type inference
                # or explicit type casting based on column dtype.
                try:
                    if pd.api.types.is_numeric_dtype(df[column]):
                        value = pd.to_numeric(value, errors='coerce')
                    elif pd.api.types.is_string_dtype(df[column]):
                        value = str(value)
                except Exception:
                    # If conversion fails, proceed with original value, comparison might still work
                    pass

                # Apply filter based on operator
                if operator == '==':
                    # Handle potential NaN values in the column before comparison
                    # Use .fillna(value_to_compare_against) or .notna() if NaN should not match
                    # For exact equality, NaN == NaN is False, so we need to be careful.
                    # If value is NaN, we want to find NaNs in the column.
                    if pd.isna(value):
                        df = df[df[column].isna()]
                    else:
                        df = df[df[column] == value]
                elif operator == '!=':
                    if pd.isna(value):
                        df = df[df[column].notna()]
                    else:
                        df = df[df[column] != value]
                elif operator == '>':
                    df = df[df[column] > value]
                elif operator == '<':
                    df = df[df[column] < value]
                elif operator == '>=':
                    df = df[df[column] >= value]
                elif operator == '<=':
                    df = df[df[column] <= value]
                elif operator == 'in':
                    if not isinstance(value, list):
                        return json.dumps({"error": f"Operador 'in' requer uma lista de valores para a coluna '{column}'."})
                    df = df[df[column].isin(value)]
                elif operator == 'not in':
                    if not isinstance(value, list):
                        return json.dumps({"error": f"Operador 'not in' requer uma lista de valores para a coluna '{column}'."})
                    df = df[~df[column].isin(value)]
                elif operator == 'contains':
                    # Ensure column is string type for .str.contains
                    if pd.api.types.is_string_dtype(df[column]):
                        df = df[df[column].str.contains(str(value), na=False)]
                    else:
                        return json.dumps({"error": f"Operador 'contains' só pode ser usado em colunas de string. Coluna '{column}' não é string."})
                else:
                    return json.dumps({"error": f"Operador '{operator}' não suportado."})

        # Convert DataFrame to a list of dictionaries for JSON output
        # Handle Timestamp and Decimal objects for JSON serialization
        for col in df.select_dtypes(include=['datetime64[ns]']).columns:
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S') # Or any other desired string format

        # Convert Decimal objects to string
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, Decimal)).any():
                df[col] = df[col].astype(str)

        result = df.to_dict(orient='records')
        result_json = json.dumps({"data": result})
        logger.info(f"query_product_data returning success: {result_json}")
        return result_json

    except Exception as e:
        error_msg = json.dumps({"error": f"Erro ao consultar dados do arquivo Parquet: {e}"})
        logger.info(f"query_product_data returning exception error: {error_msg}")
        return error_msg
