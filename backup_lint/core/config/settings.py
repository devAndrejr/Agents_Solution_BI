# core/config/settings.py
from pydantic import SecretStr, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Self
from urllib.parse import quote_plus
from sqlalchemy.engine import URL

class Settings(BaseSettings):
    """
    Centralized application settings.
    Loads values from a .env file and environment variables.
    """
    model_config = SettingsConfigDict(
        env_file="C:/Users/André/Documents/Agent_BI/.env", env_file_encoding="utf-8", extra="ignore"
    )

    # Database Configuration
    DB_USER: str = Field(..., description="Database user")
    DB_PASSWORD: SecretStr = Field(..., description="Database password")
    DB_HOST: str = Field("localhost", description="Database host")
    DB_PORT: int = Field(1433, description="Database port")
    DB_NAME: str = Field(..., description="Database name")
    DB_DRIVER: str = Field(..., description="Database driver")
    DB_TRUST_SERVER_CERTIFICATE: str = Field("yes", description="Trust server certificate")

    # LLM/OpenAI Configuration
    OPENAI_API_KEY: SecretStr = Field(..., description="OpenAI API Key")
    LLM_MODEL_NAME: str = Field("gpt-4-turbo-preview", description="Default LLM model")

    # Outras configurações da aplicação
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    ENVIRONMENT: str = Field("development", description="Application environment (development/production)")
    PARQUET_DIR: str = Field("data/parquet_cleaned", description="Directory for cleaned parquet files")

    PYODBC_CONNECTION_STRING: Optional[str] = None
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @model_validator(mode='after')
    def build_connection_strings(self) -> Self:
        # For direct pyodbc connections
        self.PYODBC_CONNECTION_STRING = (
            f"DRIVER={self.DB_DRIVER};"
            f"SERVER={self.DB_HOST};"
            f"DATABASE={self.DB_NAME};"
            f"UID={self.DB_USER};"
            f"PWD={self.DB_PASSWORD.get_secret_value()};"
            f"TrustServerCertificate={self.DB_TRUST_SERVER_CERTIFICATE};"
        )
        # For SQLAlchemy connections
        self.SQLALCHEMY_DATABASE_URI = URL.create(
            "mssql+pyodbc",
            username=self.DB_USER,
            password=self.DB_PASSWORD.get_secret_value(),
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
            query={
                "driver": self.DB_DRIVER,
                "TrustServerCertificate": self.DB_TRUST_SERVER_CERTIFICATE,
            },
        )

        return self

# Instância única para ser importada em todo o projeto
settings = Settings()