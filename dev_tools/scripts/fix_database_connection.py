#!/usr/bin/env python3
"""
Script para diagnosticar e corrigir problemas de conexão com o banco de dados
"""

import logging
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_sql_server_status():
    """
    Verifica se o SQL Server está rodando
    """
    logger.info("=== Verificando Status do SQL Server ===")

    try:
        import subprocess

        result = subprocess.run(
            ["sqlcmd", "-S", "FAMILIA\\SQLJR", "-Q", "SELECT @@VERSION"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            logger.info("✅ SQL Server está rodando e acessível")
            return True
        else:
            logger.error(f"❌ SQL Server não está acessível: {result.stderr}")
            return False

    except FileNotFoundError:
        logger.error(
            "❌ sqlcmd não encontrado. Instale SQL Server Command Line Utilities"
        )
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao verificar SQL Server: {e}")
        return False


def test_different_credentials():
    """
    Testa diferentes combinações de credenciais
    """
    logger.info("=== Testando Diferentes Credenciais ===")

    credentials_to_test = [
        {
            "server": "FAMILIA\\SQLJR",
            "database": "Projeto_Opcom",
            "username": "AgenteVirtual",
            "password": "Cacula2020",
            "driver": "ODBC+Driver+18+for+SQL+Server",
        },
        {
            "server": "FAMILIA\\SQLJR",
            "database": "Projeto_Opcom",
            "username": "sa",
            "password": "Cacula2020",
            "driver": "ODBC+Driver+18+for+SQL+Server",
        },
        {
            "server": "localhost\\SQLJR",
            "database": "Projeto_Opcom",
            "username": "AgenteVirtual",
            "password": "Cacula2020",
            "driver": "ODBC+Driver+18+for+SQL+Server",
        },
        {
            "server": "FAMILIA\\SQLJR",
            "database": "master",
            "username": "AgenteVirtual",
            "password": "Cacula2020",
            "driver": "ODBC+Driver+18+for+SQL+Server",
        },
    ]

    for i, creds in enumerate(credentials_to_test, 1):
        logger.info(
            f"Teste {i}: {creds['username']}@{creds['server']}/{creds['database']}"
        )

        try:
            from sqlalchemy import create_engine

            connection_string = (
                f"mssql+pyodbc://{creds['username']}:{creds['password']}"
                f"@{creds['server']}/{creds['database']}"
                f"?driver={creds['driver']}&TrustServerCertificate=yes"
            )

            engine = create_engine(connection_string, echo=False)

            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                result.fetchone()

            logger.info(f"✅ Teste {i} SUCESSO!")
            logger.info(f"   Credenciais funcionais encontradas:")
            logger.info(f"   Server: {creds['server']}")
            logger.info(f"   Database: {creds['database']}")
            logger.info(f"   Username: {creds['username']}")

            return creds

        except Exception as e:
            logger.warning(f"❌ Teste {i} falhou: {str(e)[:100]}...")
            continue

    logger.error("❌ Nenhuma combinação de credenciais funcionou")
    return None


def create_env_file(working_credentials):
    """
    Cria um arquivo .env com as credenciais funcionais
    """
    if not working_credentials:
        return False

    env_content = f"""# Configurações do Banco de Dados SQL Server
DB_SERVER={working_credentials['server']}
DB_NAME={working_credentials['database']}
DB_USER={working_credentials['username']}
DB_PASSWORD={working_credentials['password']}
DB_DRIVER={working_credentials['driver']}

# Configurações antigas (para compatibilidade)
MSSQL_SERVER={working_credentials['server']}
MSSQL_DATABASE={working_credentials['database']}
MSSQL_USER={working_credentials['username']}
MSSQL_PASSWORD={working_credentials['password']}
MSSQL_TRUST_SERVER_CERTIFICATE=yes
MSSQL_ENCRYPT=yes

# Configurações da API
OPENAI_API_KEY=your_openai_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# Configurações de Log
LOG_LEVEL=INFO
"""

    env_path = project_root / ".env"

    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)

        logger.info(f"✅ Arquivo .env criado em: {env_path}")
        return True

    except Exception as e:
        logger.error(f"❌ Erro ao criar arquivo .env: {e}")
        return False


def main():
    """
    Função principal
    """
    logger.info("=== Diagnóstico de Conexão com Banco de Dados ===")

    # Verifica SQL Server
    if not check_sql_server_status():
        logger.error("SQL Server não está acessível. Verifique se está rodando.")
        return False

    # Testa credenciais
    working_credentials = test_different_credentials()

    if working_credentials:
        # Cria arquivo .env
        if create_env_file(working_credentials):
            logger.info("✅ Configuração concluída com sucesso!")
            logger.info("Agora você pode executar o script de otimização.")
            return True
    else:
        logger.error("❌ Não foi possível encontrar credenciais funcionais")
        logger.error("Verifique as credenciais do SQL Server e tente novamente")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
