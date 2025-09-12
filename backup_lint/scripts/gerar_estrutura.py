import logging
import sys
from pathlib import Path

from core.utils.env_setup import setup_environment

setup_environment()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

# Itens a serem ignorados na geração da estrutura
IGNORE_LIST = {".git", ".venv", "venv", "__pycache__", "node_modules", ".vscode"}


def gerar_estrutura_diretorio(raiz: Path, nivel: int = 0, ignore_list: set = None):
    """
    Gera uma representação em árvore da estrutura de um diretório,
    ignorando itens especificados.
    """
    if ignore_list is None:
        ignore_list = IGNORE_LIST

    estrutura = ""
    prefixo = "│   " * (nivel - 1) + "├── " if nivel > 0 else ""

    try:
        # Filtra os itens a serem ignorados
        itens = sorted(
            [item for item in raiz.iterdir() if item.name not in ignore_list]
        )

        for i, item in enumerate(itens):
            conector = "└── " if i == len(itens) - 1 else "├── "
            prefixo_item = "│   " * nivel + conector
            estrutura += f"{prefixo_item}{item.name}\n"

            if item.is_dir():
                sub_prefixo = "    " if conector == "└── " else "│   "
                estrutura += f"{'│   ' * nivel}{sub_prefixo}"
                estrutura += gerar_estrutura_diretorio(item, nivel + 1, ignore_list)
    except Exception as e:
        estrutura += f"{prefixo}[ERRO ao acessar: {e}]\n"

    return estrutura


def main():
    """
    Função principal para gerar o arquivo de estrutura do projeto.
    """
    try:
        raiz_projeto = Path(__file__).resolve().parent.parent
        logging.info("Gerando estrutura do projeto a partir de: %s", raiz_projeto)

        # Usando um método mais robusto para desenhar a árvore
        arvore = ""
        itens_raiz = sorted(
            [p for p in raiz_projeto.iterdir() if p.name not in IGNORE_LIST]
        )
        for i, path in enumerate(itens_raiz):
            arvore += f"{path.name}\n"
            if path.is_dir():
                arvore += gerar_estrutura_diretorio(path)

        output_dir = raiz_projeto / "relatorios"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "estrutura_projeto.txt"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Estrutura do projeto `{raiz_projeto.name}`:\n\n{arvore}")

        logging.info("✅ Estrutura gerada com sucesso em: %s", output_file)
    except Exception as e:
        logging.error("Ocorreu um erro ao gerar a estrutura: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
