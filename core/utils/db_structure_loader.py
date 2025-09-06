import json
import logging
import os

# Configuração do logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def carregar_estrutura_banco():
    """
    Carrega a estrutura do banco a partir de 'data/database_structure.json'.

    Retorna o dicionário com o schema ou None se houver erro.
    """
    # Constrói o caminho para o arquivo de estrutura do banco de dados
    # de forma mais legível e robusta.
    current_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    caminho = os.path.join(project_root, "data", "database_structure.json")

    if not os.path.exists(caminho):
        logging.error("Arquivo de estrutura do banco não encontrado: %s", caminho)
        return None
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            estrutura = json.load(f)
        if not estrutura or not isinstance(estrutura, dict):
            logging.error("Estrutura do banco inválida ou vazia.")
            return None
        return estrutura
    except json.JSONDecodeError as e:
        logging.error("Erro ao decodificar o JSON da estrutura do banco: %s", e)
        return None
    except IOError as e:
        logging.error("Erro de I/O ao ler o arquivo de estrutura: %s", e)
        return None
    except Exception as e:
        logging.error("Erro inesperado ao carregar estrutura do banco: %s", e)
        return None


if __name__ == "__main__":
    print("Tentando carregar a estrutura do banco de dados...")
    schema = carregar_estrutura_banco()
    if schema:
        print("Estrutura do banco carregada com sucesso!")
        # Imprime apenas as chaves para não poluir a saída
        print(f"Tabelas encontradas: {list(schema.keys())}")
    else:
        print("Falha ao carregar a estrutura do banco. Verifique os logs.")
