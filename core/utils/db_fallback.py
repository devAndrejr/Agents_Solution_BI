import logging
import os
import random
import time
from functools import wraps

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
)

# Configurações de retry
MAX_RETRIES = int(os.getenv("DB_MAX_RETRIES", "3"))
BASE_DELAY = float(os.getenv("DB_RETRY_DELAY", "1.0"))  # segundos
MAX_DELAY = float(os.getenv("DB_MAX_RETRY_DELAY", "10.0"))  # segundos

# Cache para respostas de fallback
FALLBACK_RESPONSES = {
    "produto_nao_encontrado": "Não foi possível encontrar informações sobre este produto no momento. O banco de dados está temporariamente indisponível.",
    "erro_conexao": "Estou com dificuldades para acessar o banco de dados neste momento. Por favor, tente novamente mais tarde.",
    "consulta_generica": "Não foi possível processar sua consulta devido a problemas de conexão com o banco de dados.",
}


def with_db_retry(func):
    """Decorator para adicionar retry com backoff exponencial para operações de banco de dados"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0
        last_exception = None

        while retries < MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except (SQLAlchemyError, OperationalError) as e:
                last_exception = e
                retries += 1

                if retries >= MAX_RETRIES:
                    break

                # Backoff exponencial com jitter
                delay = min(
                    BASE_DELAY * (2 ** (retries - 1)) + random.uniform(0, 0.5),
                    MAX_DELAY,
                )
                logging.warning(
                    "Erro de conexão com o banco. Tentativa %d/%d. "
                    "Aguardando %.2fs.",
                    retries,
                    MAX_RETRIES,
                    delay,
                )
                logging.debug(f"Erro detalhado: {str(e)}")
                time.sleep(delay)

        # Se chegou aqui, todas as tentativas falharam
        logging.error(
            "Falha após %d tentativas de conexão com o banco: %s",
            MAX_RETRIES,
            last_exception,
        )
        raise last_exception

    return wrapper


def get_fallback_response(query_type="consulta_generica"):
    """Retorna uma resposta de fallback quando o banco de dados está indisponível"""
    return FALLBACK_RESPONSES.get(query_type, FALLBACK_RESPONSES["consulta_generica"])


def test_db_connection(connection_string):
    """Testa a conexão com o banco de dados"""
    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1")).fetchone()
            return True, "Conexão com o banco de dados estabelecida com sucesso."
    except Exception as e:
        return False, f"Erro ao conectar ao banco de dados: {str(e)}"


@with_db_retry
def execute_query_with_retry(connection_string, query, params=None):
    """Executa uma consulta SQL com retry automático em caso de falha"""
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        return result.fetchall()


def safe_db_query(
    connection_string, query, params=None, fallback_type="consulta_generica"
):
    """Executa uma consulta com tratamento de erros e fallback"""
    try:
        return execute_query_with_retry(connection_string, query, params), None
    except Exception as e:
        error_msg = f"Erro ao executar consulta: {str(e)}"
        logging.error(error_msg)
        return None, get_fallback_response(fallback_type)
