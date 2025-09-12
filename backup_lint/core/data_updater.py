import logging
import pandas as pd
import os
from core.utils.db_connection import get_db_connection # Assuming this returns a SQLAlchemy connection
from core.config.settings import settings # To get PARQUET_DIR
from typing import Dict, Any

logger = logging.getLogger(__name__)

def update_parquet_files() -> Dict[str, Any]:
    """
    Conecta ao SQL Server, lê os dados necessários e atualiza os arquivos Parquet.
    Retorna um dicionário com status e mensagem.
    """
    parquet_file_path = os.path.join(settings.PARQUET_DIR, "ADMAT_REBUILT.parquet")
    
    try:
        logger.info("Iniciando atualização dos arquivos Parquet a partir do SQL Server.")
        
        # Exemplo: Ler dados de uma tabela específica do SQL Server
        # Você precisará adaptar esta query para as suas necessidades
        sql_query = "SELECT * FROM ADMAT" # Exemplo: Substitua pela sua tabela real
        
        with get_db_connection() as conn:
            df = pd.read_sql(sql_query, conn)
        
        # Garantir que o diretório de destino existe
        os.makedirs(settings.PARQUET_DIR, exist_ok=True)
        
        # Escrever o DataFrame no arquivo Parquet
        df.to_parquet(parquet_file_path, index=False)
        
        logger.info(f"Arquivo Parquet atualizado com sucesso: {parquet_file_path}")
        return {"status": "success", "message": f"Arquivos Parquet atualizados com sucesso em {parquet_file_path}"}
        
    except Exception as e:
        logger.error(f"Erro ao atualizar arquivos Parquet: {e}", exc_info=True)
        return {"status": "error", "message": f"Erro ao atualizar arquivos Parquet: {e}"}
