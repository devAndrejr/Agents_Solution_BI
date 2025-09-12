"""
Script principal para executar o agente Caçulinha BI.
"""

import logging
import os
import sys

from core.agents.tool_agent import ToolAgent
from core.utils.env_setup import setup_environment

logging.basicConfig(level=logging.INFO)

# Adiciona o diretório raiz ao path para importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Função principal para iniciar o agente"""
    setup_environment()
    try:
        # Verifica conexão com o banco de dados
        from core.utils.db_check import check_database_connection

        if not check_database_connection():
            print(
                "[ERRO] Falha na conexão com o banco de dados. Corrija as configurações e tente novamente."
            )
            return False

        # Cria o agente BI diretamente
        agent = ToolAgent()
        if not agent:
            print("[ERRO] Não foi possível criar o agente.")
            return False

        print("\nCaçulinha BI iniciado! Digite 'sair' para encerrar.\n")

        # Loop principal para processar consultas
        while True:
            query = input("Você: ")
            if query.lower() in ["sair", "exit", "quit"]:
                print("\nCaçulinha: Até logo!")
                break

            # Processa a consulta
            response = agent.process_query(query)

            # Exibe a resposta
            if isinstance(response, dict):
                if "error" in response:
                    print(
                        f"\nCaçulinha: Desculpe, ocorreu um erro: {response['error']}"
                    )
                elif "response" in response:
                    print(f"\nCaçulinha: {response['response']}")
                else:
                    print(f"\nCaçulinha: {response}")
            else:
                print(f"\nCaçulinha: {response}")

        return True
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro ao iniciar o agente: {e}")
        return False


if __name__ == "__main__":
    try:
        # Executa a função principal do agente
        success = main()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\nErro ao iniciar o agente: {e}")
        sys.exit(1)