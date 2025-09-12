"""
Script para acionar a análise de integração do projeto e gerar um relatório.

Este script inicializa e executa o AnalisadorIntegracao, que varre o
código-fonte em busca de pontos de integração, coesão e acoplamento,
gerando um relatório detalhado em Markdown.
"""

import logging
import sys
from pathlib import Path

from core.utils.env_setup import setup_environment

setup_environment()

# Adiciona o diretório raiz do projeto ao sys.path para importações corretas
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from analise.analisador_integracao import AnalisadorIntegracao  # noqa: E402

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)


def main():
    """
    Ponto de entrada do script.

    Instancia o analisador, executa a análise completa do projeto e
    informa ao usuário a localização do relatório gerado.
    """
    logging.info("Iniciando análise de integração do projeto...")
    try:
        analisador = AnalisadorIntegracao(str(ROOT_DIR))
        caminho_relatorio = analisador.executar_analise_completa()
        logging.info("Análise concluída com sucesso.")
        logging.info("Relatório de integração gerado em: %s", caminho_relatorio)
    except Exception as e:
        logging.error("Ocorreu um erro durante a análise: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
