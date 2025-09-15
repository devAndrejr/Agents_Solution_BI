
# scripts/clean_catalog.py
import json
import re
import logging
import unicodedata
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_column_name(col_name: str) -> str:
    """
    Limpa o nome da coluna: remove acentos, caracteres especiais, espaços e converte para snake_case.
    Esta é uma versão simplificada para o catálogo, sem a lógica de unicidade.
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
    return col_name

def main():
    input_file = r"C:\Users\André\Documents\Agent_BI\data\catalog_focused.json"
    output_file = r"C:\Users\André\Documents\Agent_BI\data\catalog_cleaned.json"
    
    logger.info(f"Carregando catálogo de: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            catalog_data = json.load(f)
        logger.info("Catálogo carregado com sucesso.")
    except FileNotFoundError:
        logger.error(f"Erro: Arquivo de catálogo não encontrado em {input_file}")
        return
    except Exception as e:
        logger.error(f"Erro ao carregar o catálogo: {e}", exc_info=True)
        return

    cleaned_catalog = []
    for entry in catalog_data:
        if entry.get("file_name") == "admatao.parquet": # Focar apenas no arquivo que estamos usando
            logger.info(f"Processando entrada para {entry.get('file_name')}")
            cleaned_entry = entry.copy()
            
            # Limpar nomes no schema
            if "schema" in cleaned_entry:
                cleaned_schema = {}
                for col_name, col_type in cleaned_entry["schema"].items():
                    cleaned_schema[clean_column_name(col_name)] = col_type
                cleaned_entry["schema"] = cleaned_schema
                logger.info("Nomes de colunas no schema limpos.")

            # Limpar nomes e chaves em column_descriptions
            if "column_descriptions" in cleaned_entry:
                cleaned_descriptions = {}
                for col_name, description in cleaned_entry["column_descriptions"].items():
                    cleaned_descriptions[clean_column_name(col_name)] = description
                cleaned_entry["column_descriptions"] = cleaned_descriptions
                logger.info("Nomes de colunas em column_descriptions limpos.")
            
            cleaned_catalog.append(cleaned_entry)
        else:
            cleaned_catalog.append(entry) # Manter outras entradas como estão

    logger.info(f"Salvando catálogo limpo em: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_catalog, f, indent=4, ensure_ascii=False)
        logger.info("Catálogo limpo salvo com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao salvar o catálogo limpo: {e}", exc_info=True)

if __name__ == "__main__":
    main()
