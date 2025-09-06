import os
import pyodbc
from dotenv import load_dotenv
from pathlib import Path

# Carrega variáveis de ambiente do arquivo .env na raiz do projeto
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path, override=True)

DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER")
DB_TRUST_SERVER_CERTIFICATE = os.getenv("DB_TRUST_SERVER_CERTIFICATE")
DB_ENCRYPT = os.getenv("DB_ENCRYPT")

try:
    conn_str = (
        f"DRIVER={DB_DRIVER};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_DATABASE};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        f"TrustServerCertificate={DB_TRUST_SERVER_CERTIFICATE};"
        # f"Encrypt={DB_ENCRYPT};" # Removido temporariamente para teste
    )
    cnxn = pyodbc.connect(conn_str)
    cursor = cnxn.cursor()
    cursor.execute("SELECT 1")
    print("Conexão com SQL Server bem-sucedida!")
    cnxn.close()
except Exception as e:
    print(f"Erro na conexão com SQL Server: {e}")