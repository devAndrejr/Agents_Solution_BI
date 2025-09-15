#!/usr/bin/env python3
"""
Script para otimizar o banco de dados e configurar índices
Execute este script para melhorar a performance das consultas
"""

import logging
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import text

from core.database.sqlalchemy_connector import get_db_engine, test_connection

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def read_sql_script():
    """
    Lê o script SQL de otimização
    """
    script_path = project_root / "scripts" / "setup_database_indexes.sql"

    if not script_path.exists():
        logger.error(f"Script SQL não encontrado: {script_path}")
        return None

    with open(script_path, "r", encoding="utf-8") as f:
        return f.read()


def execute_sql_script(engine, sql_script):
    """
    Executa o script SQL no banco de dados
    """
    try:
        # Divide o script em comandos individuais
        commands = [cmd.strip() for cmd in sql_script.split("GO") if cmd.strip()]

        with engine.connect() as conn:
            for i, command in enumerate(commands, 1):
                if command:
                    logger.info(f"Executando comando {i}/{len(commands)}")
                    try:
                        result = conn.execute(text(command))
                        conn.commit()
                        logger.info(f"Comando {i} executado com sucesso")
                    except Exception as e:
                        logger.warning(f"Erro no comando {i}: {e}")
                        # Continua com o próximo comando

        logger.info("Script SQL executado com sucesso!")
        return True

    except Exception as e:
        logger.error(f"Erro ao executar script SQL: {e}")
        return False


def test_query_performance(engine):
    """
    Testa a performance das consultas após a otimização
    """
    test_queries = [
        "SELECT TOP 5 * FROM ADMAT WHERE NOME LIKE '%teste%'",
        "SELECT TOP 5 * FROM Admat_OPCOM WHERE NOME LIKE '%teste%'",
        "SELECT TOP 5 * FROM ADMAT WHERE CÓDIGO = '369947'",
        "SELECT TOP 5 * FROM Admat_OPCOM WHERE CÓDIGO = '369947'",
    ]

    logger.info("Testando performance das consultas...")

    try:
        with engine.connect() as conn:
            for i, query in enumerate(test_queries, 1):
                logger.info(f"Teste {i}: {query[:50]}...")

                import time

                start_time = time.time()

                result = conn.execute(text(query))
                rows = result.fetchall()

                end_time = time.time()
                execution_time = end_time - start_time

                logger.info(f"  - Tempo: {execution_time:.3f}s")
                logger.info(f"  - Resultados: {len(rows)} linhas")

    except Exception as e:
        logger.error(f"Erro ao testar performance: {e}")


def main():
    """
    Função principal
    """
    logger.info("=== Otimização do Banco de Dados ===")

    # Testa conexão
    logger.info("1. Testando conexão com o banco...")
    success, message = test_connection()

    if not success:
        logger.error(f"Conexão falhou: {message}")
        logger.error(
            "Verifique se o SQL Server está rodando e as credenciais estão corretas"
        )
        return False

    logger.info(f"Conexão bem-sucedida: {message}")

    # Obtém engine
    engine = get_db_engine()
    if engine is None:
        logger.error("Não foi possível obter a engine do banco")
        return False

    # Lê script SQL
    logger.info("2. Lendo script de otimização...")
    sql_script = read_sql_script()
    if sql_script is None:
        return False

    # Executa script
    logger.info("3. Executando script de otimização...")
    if not execute_sql_script(engine, sql_script):
        return False

    # Testa performance
    logger.info("4. Testando performance...")
    test_query_performance(engine)

    logger.info("=== Otimização concluída com sucesso! ===")
    logger.info("Agora as consultas devem ser muito mais rápidas.")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
