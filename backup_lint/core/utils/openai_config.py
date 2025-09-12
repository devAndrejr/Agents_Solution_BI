import logging

# Configura o logging para este módulo
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def configure_openai():
    """
    Configura o cliente da OpenAI.
    Atualmente, esta função é um placeholder. A lógica para carregar a chave
    de API e instanciar o cliente deve ser adicionada aqui.
    """
    logging.info("Configurando o cliente OpenAI...")
    # Exemplo de como a configuração poderia ser:
    # from openai import OpenAI
    # import os
    #
    # api_key = os.getenv("OPENAI_API_KEY")
    # if not api_key:
    #     logging.error("A variável de ambiente OPENAI_API_KEY não foi definida.")
    #     return None
    #
    # client = OpenAI(api_key=api_key)
    # logging.info("Cliente OpenAI configurado com sucesso.")
    # return client
    logging.warning("Configuração do cliente OpenAI " "não implementada.")
    return None


if __name__ == "__main__":
    print("Executando script de configuração do OpenAI...")
    configure_openai()
    print("Script concluído.")
