# check_db.py
import os
import pyodbc
from dotenv import load_dotenv

print("--- Iniciando teste de conexão de banco de dados mínimo ---")

# Carrega as variáveis do arquivo .env
# Isso garante que estamos lendo os valores mais recentes
load_dotenv(override=True)

# Pega as credenciais diretamente do ambiente
db_driver = os.getenv("DB_DRIVER")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_trust = os.getenv("DB_TRUST_SERVER_CERTIFICATE")

# Imprime as variáveis para garantir que foram lidas corretamente
# (Verifique se a senha impressa parece correta em termos de comprimento)
print(f"Driver: {db_driver}")
print(f"Host: {db_host}")
print(f"Porta: {db_port}")
print(f"Banco: {db_name}")
print(f"Usuário: {db_user}")
print(f"Senha: {'*' * len(db_password) if db_password else 'Nenhuma'}")
print(f"Trust Cert: {db_trust}")


# Monta a string de conexão
conn_str = (
    f"DRIVER={db_driver};"
    f"SERVER={db_host},{db_port};"
    f"DATABASE={db_name};"
    f"UID={db_user};"
    f"PWD={db_password};"
    f"TrustServerCertificate={db_trust};"
)

print("\nTentando conectar com a string:")
print(conn_str)

try:
    # Tenta conectar
    cnxn = pyodbc.connect(conn_str, timeout=10)
    print("\n\033[92m" + "="*50)
    print("CONEXÃO BEM-SUCEDIDA!")
    print("="*50 + "\033[0m")
    cnxn.close()

except Exception as e:
    print("\n\033[91m" + "="*50)
    print("FALHA NA CONEXÃO.")
    print(f"Erro: {e}")
    print("="*50 + "\033[0m")

print("\n--- Teste finalizado ---")