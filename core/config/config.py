import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


class Config:
    """
    Classe central de configuração para o projeto.
    Carrega variáveis de ambiente de um arquivo .env e as expõe como atributos de classe.
    """

    # Carrega variáveis de ambiente do arquivo .env na raiz do projeto
    dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=True)
    else:
        # Em um ambiente de produção ou CI/CD, as variáveis podem ser definidas diretamente.
        # Adicionamos um log ou print para alertar que o .env não foi encontrado.
        print(
            f"Aviso: Arquivo .env não encontrado em '{dotenv_path}'. As configurações dependerão das variáveis de ambiente do sistema."
        )

    # Configurações do banco de dados
    DB_SERVER = os.getenv("DB_HOST", "localhost")
    DB_DATABASE = os.getenv("DB_NAME", "nome_do_banco")
    DB_USER = os.getenv("DB_USER", "usuario")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "senha")
    DB_PORT = os.getenv("DB_PORT", "1433")
    DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    DB_TRUST_SERVER_CERTIFICATE = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")
    DB_ENCRYPT = os.getenv("DB_ENCRYPT", "no")

    # String de conexão para SQLAlchemy, construída dinamicamente
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Gera a string de conexão do SQLAlchemy a partir das variáveis de ambiente.
        A senha é escapada para garantir que a URL seja válida.
        """
        password_quoted = quote_plus(self.DB_PASSWORD) if self.DB_PASSWORD else ""
        driver_quoted = quote_plus(self.DB_DRIVER)

        return (
            f"mssql+pyodbc://{self.DB_USER}:{password_quoted}@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_DATABASE}?"
            f"driver={driver_quoted}&TrustServerCertificate={self.DB_TRUST_SERVER_CERTIFICATE}"
            + (f"&Encrypt={self.DB_ENCRYPT}" if self.DB_ENCRYPT.lower() == "yes" else "")
        )

    # Modo de demonstração (sem acesso ao banco de dados)
    DEMO_MODE = os.getenv("DEMO_MODE", "False").lower() == "true"

    # Configurações da aplicação
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "chave_secreta_padrao")
    SESSION_COOKIE_PATH = "/"

    # OpenAI API Key and Model Name
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")

    # Configurações de log
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # LangSmith Tracing
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "caculinha-bi-project")


# Para manter a compatibilidade com o resto do código que pode estar importando
# as variáveis diretamente, podemos instanciar a classe aqui.
# No entanto, a prática recomendada seria importar a classe `Config` e usar `Config.VARIAVEL`.
# Por agora, faremos a instância para minimizar quebras.
config = Config()

# Exportando variáveis para compatibilidade com o código legado que pode fazer `from core.config.config import DEBUG`
DEBUG = config.DEBUG
SECRET_KEY = config.SECRET_KEY
DEMO_MODE = config.DEMO_MODE
OPENAI_API_KEY = config.OPENAI_API_KEY
LLM_MODEL_NAME = config.LLM_MODEL_NAME
LOG_LEVEL = config.LOG_LEVEL
SQLALCHEMY_DATABASE_URI = config.SQLALCHEMY_DATABASE_URI

# Exportando variáveis do banco de dados para compatibilidade
DB_SERVER = config.DB_SERVER
DB_DATABASE = config.DB_DATABASE
DB_USER = config.DB_USER
DB_PASSWORD = config.DB_PASSWORD
DB_PORT = config.DB_PORT
DB_DRIVER = config.DB_DRIVER
DB_TRUST_SERVER_CERTIFICATE = config.DB_TRUST_SERVER_CERTIFICATE
DB_ENCRYPT = config.DB_ENCRYPT
