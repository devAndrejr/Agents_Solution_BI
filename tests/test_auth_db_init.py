import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import sql_server_auth_db as auth_db
from core.config.config import Config # Para garantir que as variáveis de ambiente sejam carregadas

# Garante que as variáveis de ambiente sejam carregadas
_ = Config()

try:
    auth_db.init_db()
    print("auth_db.init_db() executado com sucesso!")
except Exception as e:
    print(f"Erro ao executar auth_db.init_db(): {e}")