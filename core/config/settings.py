from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import urllib

class Settings(BaseSettings):
    """
    Centraliza as configurações da aplicação, carregando variáveis de um ficheiro .env.
    Esta versão foi refatorada para ser mais robusta, construindo a connection string
    diretamente a partir das variáveis de ambiente.
    """
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8',
        extra='ignore' # Ignora variáveis extras no .env
    )

    # Variáveis de ambiente individuais para a base de dados
    DB_SERVER: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_DRIVER: str = "{ODBC Driver 17 for SQL Server}" # Valor padrão comum
    DB_TRUST_SERVER_CERTIFICATE: bool = False

    # Chave da API para o LLM
    OPENAI_API_KEY: SecretStr
    
    @computed_field
    @property
    def SQL_SERVER_CONNECTION_STRING(self) -> str:
        """
        Gera a string de conexão para SQLAlchemy (mssql+pyodbc).
        """
        driver_formatted = self.DB_DRIVER.replace(' ', '+')
        password_quoted = urllib.parse.quote_plus(self.DB_PASSWORD.get_secret_value())
        
        conn_str = (
            f"mssql+pyodbc://{self.DB_USER}:{password_quoted}@"
            f"{self.DB_SERVER}/{self.DB_NAME}?"
            f"driver={driver_formatted}"
        )
        if self.DB_TRUST_SERVER_CERTIFICATE:
            conn_str += "&TrustServerCertificate=yes"
        
        return conn_str

    @computed_field
    @property
    def PYODBC_CONNECTION_STRING(self) -> str:
        """
        Gera a string de conexão ODBC para uso direto com pyodbc.
        """
        conn_str = (
            f"DRIVER={self.DB_DRIVER};"
            f"SERVER={self.DB_SERVER};"
            f"DATABASE={self.DB_NAME};"
            f"UID={self.DB_USER};"
            f"PWD={self.DB_PASSWORD.get_secret_value()}"
        )
        if self.DB_TRUST_SERVER_CERTIFICATE:
            conn_str += ";TrustServerCertificate=yes"
            
        return conn_str

# Instância única das configurações para ser usada em toda a aplicação
settings = Settings()