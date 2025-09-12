import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Cache para armazenar DataFrames carregados
_df_cache = {}

def get_table_df(table_name, filters=None, parquet_dir="data/parquet_cleaned"):
    # Ignora o table_name e carrega sempre o catálogo mestre
    master_file_name = "master_catalog.parquet"
    file_path = os.path.join(parquet_dir, master_file_name)
    
    # Verifica se o DataFrame já está no cache
    if file_path in _df_cache:
        logger.info(f"Carregando DataFrame mestre do cache.")
        df = _df_cache[file_path].copy() # Retorna uma cópia para evitar modificações no cache
    else:
        logger.info(f"Tentando ler o arquivo Parquet mestre: {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"Arquivo Parquet mestre não encontrado: {file_path}")
            return None
        try:
            df = pd.read_parquet(file_path)
            _df_cache[file_path] = df.copy() # Armazena uma cópia no cache
            logger.info(f"Arquivo {master_file_name} lido e cacheado com sucesso. {len(df)} linhas.")
        except Exception as e:
            logger.error(f"Erro ao ler o Parquet mestre {file_path}: {e}")
            return None

    if filters:
        for col, val in filters.items():
            if col in df.columns:
                df = df[df[col] == val]
        logger.info(f"Filtros aplicados. {len(df)} linhas após filtro.")
    
    return df

def prepare_chart_data(df, x_col, y_col, chart_type="bar", title=None):
    if df is None or x_col not in df.columns or y_col not in df.columns:
        return {
            "data": [],
            "layout": {"title": title or "Gráfico"},
            "error": (
                f"Colunas {x_col} ou {y_col} não encontradas."
            )
        }
    try:
        # Ordena o DataFrame pela coluna do eixo X se for um gráfico de linha
        if chart_type == 'line':
            df = df.sort_values(by=x_col)

        data = [
            {
                "x": df[x_col].tolist(),
                "y": df[y_col].tolist(),
                "type": chart_type,
                "name": y_col,
            }
        ]
        layout = {"title": title or f"{y_col} por {x_col}"}
        return {"data": data, "layout": layout}
    except Exception as e:
        logger.error(f"Erro ao preparar dados do gráfico: {e}")
        return {
            "data": [],
            "layout": {"title": title or "Gráfico"},
            "error": str(e)
        }