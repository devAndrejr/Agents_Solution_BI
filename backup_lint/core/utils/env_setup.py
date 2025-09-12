import logging
from pathlib import Path

from dotenv import load_dotenv

"""
Configuração de ambiente
"""


def setup_environment(base_dir=None):
    """
    Carrega o arquivo .env do diretório raiz do projeto e, se existir,
    também carrega o arquivo .env específico em core/config/.env, permitindo
    que variáveis definidas lá (como SQLALCHEMY_DATABASE_URI) sobreponham as anteriores.
    """
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent.parent
    else:
        base_dir = Path(base_dir)

    # 1) .env na raiz
    dotenv_root = base_dir / ".env"
    if dotenv_root.exists():
        load_dotenv(dotenv_path=dotenv_root, override=True)
        logging.info(f"Arquivo .env carregado com sucesso de {dotenv_root}")
    else:
        logging.warning(
            f"Arquivo .env não encontrado em {dotenv_root}. Variáveis de ambiente dependerão do sistema."
        )

    # 2) .env em core/config/.env (opcional)
    dotenv_config = base_dir / "core" / "config" / ".env"
    if dotenv_config.exists():
        load_dotenv(dotenv_path=dotenv_config, override=True)
        logging.info(f"Arquivo .env adicional carregado de {dotenv_config}")


if __name__ == "__main__":
    print("Rodando como script...")
    setup_environment()
