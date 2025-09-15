
# scripts/clean_parquet_data.py
import pandas as pd
import re
import logging
import os
import unicodedata

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_column_name(col_name: str, existing_names: set) -> str:
    """
    Limpa o nome da coluna: remove acentos, caracteres especiais, espaços e converte para snake_case.
    Garante que o nome seja único adicionando um sufixo se necessário.
    """
    # Remover acentos
    col_name = str(unicodedata.normalize('NFKD', col_name).encode('ascii', 'ignore').decode('utf-8'))
    # Substituir caracteres especiais e espaços por underscore
    col_name = re.sub(r'[^a-zA-Z0-9_]', '', col_name) # Remove tudo que não é alfanumérico ou underscore
    col_name = re.sub(r'\s+', '_', col_name) # Substitui espaços por underscore
    col_name = re.sub(r'[^a-zA-Z0-9_]', '', col_name) # Remove caracteres especiais restantes
    # Converter para snake_case (se houver maiúsculas)
    col_name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', col_name).lower()
    # Remover underscores duplicados ou no início/fim
    col_name = re.sub(r'_+', '_', col_name).strip('_')

    # Garantir unicidade
    original_col_name = col_name
    counter = 1
    while col_name in existing_names:
        col_name = f"{original_col_name}_{counter}"
        counter += 1
    return col_name

def clean_and_convert_datatypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte colunas para os tipos de dados corretos, tratando erros.
    """
    logger.info("Iniciando conversão de tipos de dados...")
    for col in df.columns:
        # Tentar converter para numérico
        if pd.api.types.is_object_dtype(df[col]): # Corrected line
            try:
                # Tenta converter para numérico, coercing errors para NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
                logger.info(f"Coluna '{col}' convertida para numérico.")
            except Exception:
                pass # Não é numérico, tentar outras conversões
        
        # Tentar converter para datetime
        if pd.api.types.is_object_dtype(df[col]): # Corrected line
            try:
                # Tenta converter para datetime, coercing errors para NaT
                df[col] = pd.to_datetime(df[col], errors='coerce')
                logger.info(f"Coluna '{col}' convertida para datetime.")
            except Exception:
                pass # Não é datetime, manter como object

    return df

def main():
    file_path = r"C:\Users\André\Documents\Agent_BI\data\parquet_cleaned\admatao.parquet"
    logger.info(f"Carregando arquivo Parquet de: {file_path}")
    
    try:
        df = pd.read_parquet(file_path)
        logger.info(f"Arquivo carregado. Shape original: {df.shape}")

        # 1. Limpar nomes das colunas
        original_columns = df.columns.tolist()
        cleaned_columns = []
        seen_names = set()
        for col in df.columns:
            cleaned_name = clean_column_name(col, seen_names)
            cleaned_columns.append(cleaned_name)
            seen_names.add(cleaned_name)
        df.columns = cleaned_columns
        logger.info("Nomes das colunas limpos.")
        for old, new in zip(original_columns, df.columns):
            if old != new:
                logger.info(f"  Renomeado: '{old}' -> '{new}'")

        # 2. Converter tipos de dados
        df = clean_and_convert_datatypes(df)
        logger.info("Tipos de dados convertidos.")

        # 3. Salvar o arquivo limpo
        df.to_parquet(file_path, index=False)
        logger.info(f"Arquivo Parquet limpo salvo em: {file_path}")
        logger.info("Análise de tipos de dados após limpeza:")
        for col, dtype in df.dtypes.items():
            logger.info(f"  - {col}: {dtype}")

    except FileNotFoundError:
        logger.error(f"Erro: Arquivo Parquet não encontrado em {file_path}")
    except Exception as e:
        logger.error(f"Erro durante o processo de limpeza: {e}", exc_info=True)

if __name__ == "__main__":
    main()
