from sqlalchemy import create_engine
from core.config.settings import settings # Import the new settings object

# A URI da base de dados é agora obtida diretamente do objeto de configurações centralizado.
DATABASE_URI = settings.SQL_SERVER_CONNECTION_STRING

# Create the SQLAlchemy engine with connection pooling
engine = create_engine(DATABASE_URI, pool_size=10, max_overflow=20)

def get_db_connection():
    """
    Retorna uma conexão com o banco de dados SQL Server do pool de conexões do SQLAlchemy.
    """
    return engine.connect()
