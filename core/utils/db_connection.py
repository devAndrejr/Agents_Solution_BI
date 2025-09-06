from sqlalchemy import create_engine
from core.config.config import Config

# Get the SQLAlchemy database URI from the Config class
DATABASE_URI = Config().SQLALCHEMY_DATABASE_URI

# Create the SQLAlchemy engine with connection pooling
# pool_size: the number of connections to keep open in the pool
# max_overflow: the number of connections that can be opened beyond the pool_size
engine = create_engine(DATABASE_URI, pool_size=10, max_overflow=20)

def get_db_connection():
    """
    Retorna uma conexão com o banco de dados SQL Server do pool de conexões do SQLAlchemy.
    """
    return engine.connect()