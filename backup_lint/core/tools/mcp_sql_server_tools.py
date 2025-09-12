# core/tools/mcp_sql_server_tools.py
import os
import pandas as pd
from typing import Dict, Any, Optional
from langchain_core.tools import tool
import logging

# Caminho para o arquivo Parquet agora aponta para a nova fonte de dados
PARQUET_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'parquet_cleaned')
ADMATAO_PATH = os.path.join(PARQUET_DIR, 'admatao.parquet')

@tool
def get_product_data(product_code: str) -> Dict[str, Any]:
    """
    Busca dados de um produto específico a partir do arquivo Parquet 'admatao.parquet'.
    Recebe um 'product_code' e retorna um dicionário com os dados do produto.
    """
    logging.info(f"Buscando dados para o produto: {product_code} no arquivo Parquet 'admatao.parquet'.")
    
    try:
        if not os.path.exists(ADMATAO_PATH):
            logging.error(f"Arquivo Parquet não encontrado em: {ADMATAO_PATH}")
            return {"error": "Fonte de dados de produtos (admatao.parquet) não encontrada."}

        df = pd.read_parquet(ADMATAO_PATH)
        
        # Usa a coluna correta 'PRODUTO' e a converte para string para a comparação
        df['PRODUTO'] = df['PRODUTO'].astype(str)
        product_code = str(product_code)

        product_info = df[df['PRODUTO'] == product_code]

        if product_info.empty:
            return {"data": f"Nenhum produto encontrado com o código {product_code}."}
        
        # Converte o resultado para um dicionário para retornar
        return {"data": product_info.to_dict(orient='records')}

    except Exception as e:
        logging.error(f"Erro ao ler o arquivo Parquet ou processar os dados: {e}", exc_info=True)
        return {"error": f"Ocorreu um erro inesperado ao buscar dados do produto: {e}"}

@tool
def get_product_stock_rupture(product_id: int) -> Dict[str, Any]:
    """
    Identifica as unidades de negócio (UNEs) onde um produto específico está em ruptura de estoque (estoque <= 0).
    Recebe um 'product_id' e retorna uma lista de UNEs com ruptura de estoque.
    """
    logging.info(f"Verificando ruptura de estoque para o produto: {product_id}")
    try:
        if not os.path.exists(ADMATAO_PATH):
            logging.error(f"Arquivo Parquet não encontrado em: {ADMATAO_PATH}")
            return {"error": "Fonte de dados de produtos (admatao.parquet) não encontrada."}

        df = pd.read_parquet(ADMATAO_PATH)
        
        df['PRODUTO'] = df['PRODUTO'].astype(str)
        df['ESTOQUE_UNE'] = pd.to_numeric(df['ESTOQUE_UNE'], errors='coerce').fillna(0)
        product_id_str = str(product_id)

        product_df = df[df['PRODUTO'] == product_id_str]

        if product_df.empty:
            return {"data": f"Nenhum produto encontrado com o ID {product_id}."}

        rupture_df = product_df[product_df['ESTOQUE_UNE'] <= 0]

        if rupture_df.empty:
            return {"data": f"Produto com ID {product_id} não apresenta ruptura de estoque em nenhuma UNE."}

        rupture_unes = rupture_df[['UNE', 'UNE_NOME', 'ESTOQUE_UNE']].to_dict(orient='records')
        
        return {"data": {"product_id": product_id, "rupture_locations": rupture_unes}}

    except Exception as e:
        logging.error(f"Erro ao verificar ruptura de estoque: {e}", exc_info=True)
        return {"error": f"Ocorreu um erro inesperado ao verificar a ruptura de estoque: {e}"}
@tool
def list_product_categories() -> Dict[str, Any]:
    """
    Retorna uma lista de todas as categorias de produtos disponíveis no arquivo Parquet 'admatao.parquet'.
    """
    logging.info(f"Listando categorias de produtos do arquivo Parquet 'admatao.parquet'.")
    try:
        if not os.path.exists(ADMATAO_PATH):
            logging.error(f"Arquivo Parquet não encontrado em: {ADMATAO_PATH}")
            return {"error": "Fonte de dados de produtos (admatao.parquet) não encontrada."}

        df = pd.read_parquet(ADMATAO_PATH)
        
        # Assumindo que a coluna de categoria se chama 'CATEGORIA'
        if 'CATEGORIA' not in df.columns:
            return {"error": "Coluna 'CATEGORIA' não encontrada no arquivo admatao.parquet."}

        categories = df['CATEGORIA'].unique().tolist()
        return {"data": {"categories": categories}}

    except Exception as e:
        logging.error(f"Erro ao listar categorias de produtos: {e}", exc_info=True)
        return {"error": f"Ocorreu um erro inesperado ao listar categorias de produtos: {e}"}

SALES_DATA_PATH = os.path.join(PARQUET_DIR, 'vendas.parquet')

@tool
def get_last_sale_date(product_id: int) -> Dict[str, Any]:
    """
    Retorna a data da última venda de um produto específico a partir do arquivo Parquet 'vendas.parquet'.
    Recebe um 'product_id' e retorna um dicionário com a data da última venda.
    """
    logging.info(f"Buscando data da última venda para o produto: {product_id} no arquivo Parquet 'vendas.parquet'.")
    try:
        if not os.path.exists(SALES_DATA_PATH):
            logging.error(f"Arquivo Parquet de vendas não encontrado em: {SALES_DATA_PATH}")
            return {"error": "Fonte de dados de vendas (vendas.parquet) não encontrada."}

        df_sales = pd.read_parquet(SALES_DATA_PATH)
        
        # Assumindo que 'produto_id' é o ID do produto e 'data_venda' é a coluna de data da venda
        df_sales['produto_id'] = df_sales['produto_id'].astype(str)
        product_id_str = str(product_id)
        df_sales['data_venda'] = pd.to_datetime(df_sales['data_venda'])

        product_sales = df_sales[df_sales['produto_id'] == product_id_str]

        if product_sales.empty:
            return {"data": f"Nenhuma venda encontrada para o produto com ID {product_id}."}
        
        last_sale_date = product_sales['data_venda'].max() # Pega a data mais recente
        return {"data": {"product_id": product_id, "last_sale_date": last_sale_date.strftime('%Y-%m-%d')}}

    except Exception as e:
        logging.error(f"Erro ao buscar a data da última venda do produto: {e}", exc_info=True)
        return {"error": f"Ocorreu um erro inesperado ao buscar a data da última venda do produto: {e}"}

# A lista de ferramentas agora reflete a nova arquitetura.
sql_tools = [
    get_product_data,
    get_product_stock_rupture,
    list_product_categories,
    get_last_sale_date,
]