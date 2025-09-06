import logging
from pathlib import Path

from dotenv import load_dotenv

"""
Configuração de ambiente
"""


def setup_environment(base_dir=None):
    """
    Carrega o arquivo .env do diretório raiz do projeto ou de base_dir,
    se fornecido.
    """
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent.parent
    else:
        base_dir = Path(base_dir)
    dotenv_path = base_dir / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=True)
        logging.info(f"Arquivo .env carregado com sucesso de {dotenv_path}")
    else:
        logging.warning(
            f"Arquivo .env não encontrado em {dotenv_path}. "
            "Variáveis de ambiente dependerão do sistema."
        )


if __name__ == "__main__":
    print("Rodando como script...")
    setup_environment()
