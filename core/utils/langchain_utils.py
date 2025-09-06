import logging
import os

from langchain.chat_models import ChatOpenAI

"""
Utilitários para integração com LangChain
"""


def get_langchain_model(model_name=None, temperature=None):
    """
    Retorna um modelo LangChain configurado

    Args:
        model_name (str): Nome do modelo a ser usado
        temperature (float): Temperatura para geração

    Returns:
        ChatOpenAI: Modelo LangChain configurado
    """
    try:
        # Configura a chave da API OpenAI
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            logging.error("Chave da API OpenAI não configurada")
            return None

        # Usa os valores padrão se não fornecidos
        if not model_name:
            model_name = os.getenv("LLM_MODEL", "gpt-4")

        if not temperature:
            temperature = float(os.getenv("LLM_TEMPERATURE", "0"))

        # Inicializa o modelo LangChain
        # Não inclui o parâmetro "proxies" que estava causando o erro
        chat = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=api_key,
            verbose=True,
        )

        return chat

    except Exception as e:
        logging.error(f"Erro ao criar modelo LangChain: {e}")
        return None


if __name__ == "__main__":
    print("Rodando como script...")
    # TODO: Adicionar chamada a uma função principal se necessário
