# scripts/data_pipeline.py
import os
import logging
import pandas as pd
import argparse
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from typing import Dict

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataPipeline:
    """
    Responsável por extrair dados do SQL Server e salvá-los como arquivos Parquet.
    """
    def __init__(self, db_params: Dict[str, str]):
        """
        Inicializa o pipeline com os parâmetros do banco de dados.
        """
        self.engine = self._create_db_engine(db_params)
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'parquet_cleaned')
        os.makedirs(self.output_dir, exist_ok=True)

    def _create_db_engine(self, db_params: Dict[str, str]):
        """
        Cria a engine do SQLAlchemy a partir dos parâmetros fornecidos.
        """
        # Criptografa a senha para uso seguro na URL de conexão
        password_encoded = quote_plus(db_params['password'])
        
        conn_str = (
            f"mssql+pyodbc://{db_params['user']}:{password_encoded}@"
            f"{db_params['server']}/{db_params['database']}?driver=ODBC+Driver+17+for+SQL+Server"
        )
        
        logging.info("Criando engine de conexão com o banco de dados.")
        return create_engine(conn_str)

    def _extract_table_to_parquet(self, table_name: str, output_filename: str):
        """
        Extrai todos os dados de uma tabela e salva em um arquivo Parquet.
        """
        output_path = os.path.join(self.output_dir, output_filename)
        logging.info(f"Iniciando extração da tabela '{table_name}' para '{output_path}'...")

        try:
            with self.engine.connect() as connection:
                query = text(f'SELECT * FROM {table_name}')
                df = pd.read_sql(query, connection)
                
                if df.empty:
                    logging.warning(f"A tabela '{table_name}' está vazia ou não retornou dados.")
                    return

                df.to_parquet(output_path, index=False, compression='snappy')
                logging.info(f"Tabela '{table_name}' extraída com sucesso. {len(df)} linhas salvas em '{output_path}'.")

        except Exception as e:
            logging.error(f"Falha ao extrair a tabela '{table_name}'. Erro: {e}", exc_info=True)
            raise

    def run(self):
        """
        Executa o pipeline de dados para a tabela consolidada.
        """
        logging.info("Iniciando a execução do pipeline de dados...")
        try:
            self._extract_table_to_parquet('dbo.ADMMATAO', 'admatao.parquet')
            logging.info("Pipeline de dados concluído com sucesso.")
        except Exception as e:
            logging.error(f"Ocorreu um erro durante a execução do pipeline: {e}")

def main():
    """
    Função principal para executar o script via linha de comando.
    """
    parser = argparse.ArgumentParser(description="Pipeline de Dados para o Caçulinha BI.")
    parser.add_argument("--server", required=True, help="Endereço do servidor SQL.")
    parser.add_argument("--database", required=True, help="Nome do banco de dados.")
    parser.add_argument("--user", required=True, help="Nome de usuário para o banco.")
    parser.add_argument("--password", required=True, help="Senha para o banco de dados.")
    
    args = parser.parse_args()
    
    db_params = {
        "server": args.server,
        "database": args.database,
        "user": args.user,
        "password": args.password
    }
    
    pipeline = DataPipeline(db_params=db_params)
    pipeline.run()

if __name__ == '__main__':
    main()
