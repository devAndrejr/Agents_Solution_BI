# tests/verify_config_and_connection.py
import pyodbc
from core.config.settings import settings

print("--- Iniciando teste de conexão com a nova arquitetura ---")

print("\n1. Verificando as configurações carregadas de .env...")
try:
    print(f"DB_SERVER: {settings.DB_SERVER}")
    print(f"DB_NAME: {settings.DB_NAME}")
    print(f"DB_USER: {settings.DB_USER}")
    print(f"DB_PASSWORD: {'*' * len(settings.DB_PASSWORD.get_secret_value())}")
    print(f"DB_TRUST_SERVER_CERTIFICATE: {settings.DB_TRUST_SERVER_CERTIFICATE}")
    print("Configurações carregadas com sucesso!")
except Exception as e:
    print(f"\033[91mErro ao carregar as configurações: {e}\033[0m")
    print("Verifique se o arquivo .env existe e contém as variáveis corretas (DB_SERVER, DB_NAME, etc.).")
    exit()

print("\n2. Tentando conectar ao banco de dados usando a string de conexão gerada...")
conn_str = settings.PYODBC_CONNECTION_STRING
print(f"String de conexão usada (senha omitida): {conn_str.replace(settings.DB_PASSWORD.get_secret_value(), '********')}")

try:
    cnxn = pyodbc.connect(conn_str, timeout=10)
    print("\n\033[92m" + "="*50)
    print("CONEXÃO BEM-SUCEDIDA!")
    print("="*50 + "\033[0m")
    cnxn.close()
    print("\nTeste TC-CONFIG-01: Aprovado")

except Exception as e:
    print("\n\033[91m" + "="*50)
    print("FALHA NA CONEXÃO.")
    print(f"Erro: {e}")
    print("="*50 + "\033[0m")
    print("\nPossíveis causas:")
    print("- As credenciais no arquivo .env (DB_SERVER, DB_NAME, etc.) estão incorretas.")
    print("- O servidor do banco de dados está inacessível (firewall, rede).")
    print("\nTeste TC-CONFIG-01: Falhou")

print("\n--- Teste finalizado ---")
