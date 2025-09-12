import logging
import os
import re

import pandas as pd
from sqlalchemy import create_engine, text

"""
Utilitários para consultas SQL
"""


def get_connection_string():
    """
    Obtém a string de conexão com o banco de dados

    Returns:
        str: String de conexão para SQLAlchemy
    """
    # Tenta obter a string de conexão diretamente do ambiente
    connection_string = os.getenv("SQLALCHEMY_DATABASE_URI")

    if connection_string:
        logging.info("Usando string de conexão do ambiente")
        return connection_string

    # Se não encontrar, constrói a partir dos components
    db_server = os.getenv("DB_SERVER", "localhost")
    db_name = os.getenv("DB_DATABASE", "Projeto_Opcom")
    db_user = os.getenv("DB_USER", "AgenteVirtual")
    db_password = os.getenv("DB_PASSWORD", "Cacula@2020")
    os.getenv("DB_PORT", "1433")
    db_driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    trust_cert = os.getenv("DB_TRUST_CERTIFICATE", "yes")

    # Constrói a string de conexão
    try:
        # Método 1: String de conexão direta
        connection_string = f"mssql+pyodbc://{db_user}:{db_password}@{db_server}/{db_name}?driver={db_driver.replace(' ', '+')}&TrustServerCertificate={trust_cert}"

        # Método 2: String de conexão com URL encoding (alternativa)
        # connection_string = (
        #     "mssql+pyodbc:///?odbc_connect=" +
        #     quote_plus(
        #         f"DRIVER={{{db_driver}}};"
        #         f"SERVER={db_server};"
        #         f"DATABASE={db_name};"
        #         f"UID={db_user};PWD={db_password};"
        #         f"TrustServerCertificate={trust_cert}"
        #     )
        # )

        logging.info("String de conexão construída a partir dos components")
        return connection_string

    except Exception as e:
        logging.error(f"Erro ao construir string de conexão: {e}")
        return None


def verificar_operacoes_proibidas(query, operacoes_proibidas=None):
    """
    Verifica se a consulta contém operações proibidas

    Args:
        query (str): Consulta SQL
        operacoes_proibidas (list): Lista de operações proibidas

    Returns:
        bool: True se a consulta contiver operações proibidas, False caso contrário
    """
    if not operacoes_proibidas:
        operacoes_proibidas = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "ALTER",
            "CREATE",
            "EXEC",
            "EXECUTE",
        ]

    # Converte a consulta para minúsculas para facilitar a comparação
    query_lower = query.lower()

    # Verifica cada operação proibida
    for operacao in operacoes_proibidas:
        # Verifica se a operação aparece como uma palavra completa
        padrao = r"\b" + operacao.lower() + r"\b"
        if re.search(padrao, query_lower):
            logging.warning(f"Operação proibida detectada na consulta: {operacao}")
            return True

    return False


def formatar_consulta_sql(query):
    """
    Formata uma consulta SQL para melhor legibilidade

    Args:
        query (str): Consulta SQL

    Returns:
        str: Consulta SQL formatada
    """
    # Remove espaços extras
    query = re.sub(r"\s+", " ", query).strip()

    # Adiciona quebras de linha após palavras-chave comuns
    palavras_chave = [
        "SELECT",
        "FROM",
        "WHERE",
        "GROUP BY",
        "ORDER BY",
        "HAVING",
        "JOIN",
        "LEFT JOIN",
        "RIGHT JOIN",
        "INNER JOIN",
        "OUTER JOIN",
        "UNION",
        "INTERSECT",
        "EXCEPT",
    ]

    for palavra in palavras_chave:
        # Substitui a palavra-chave por uma quebra de linha seguida da palavra-chave
        query = re.sub(
            r"\b" + palavra + r"\b", "\n" + palavra, query, flags=re.IGNORECASE
        )

    return query


def executar_consulta(query, params=None, max_rows=1000):
    """
    Executa uma consulta SQL e retorna os resultados como DataFrame

    Args:
        query (str): Consulta SQL a ser executada
        params (dict): Parâmetros para a consulta
        max_rows (int): Número máximo de linhas a retornar

    Returns:
        pandas.DataFrame: Resultados da consulta
    """
    # Verifica se a consulta contém operações proibidas
    if verificar_operacoes_proibidas(query):
        logging.error("Consulta contém operações proibidas")
        raise ValueError("Operação não permitida na consulta SQL")

    # Obtém a string de conexão
    connection_string = get_connection_string()

    if not connection_string:
        logging.error("String de conexão não disponível")
        raise ValueError(
            "Não foi possível obter a string de conexão com o banco de dados"
        )

    try:
        # Cria o engine do SQLAlchemy
        engine = create_engine(connection_string)

        # Executa a consulta
        with engine.connect() as conn:
            # Se houver parâmetros, usa-os na consulta
            if params:
                result = conn.execute(text(query), params)
            else:
                result = conn.execute(text(query))

            # Obtém os resultados
            columns = result.keys()
            rows = result.fetchmany(max_rows)

            # Converte para DataFrame
            df = pd.DataFrame(rows, columns=columns)

            return df

    except Exception as e:
        logging.error(f"Erro ao executar consulta SQL: {e}")
        raise
