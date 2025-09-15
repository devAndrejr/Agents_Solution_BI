import logging
from openai import OpenAI
# CORREÇÃO: A importação de 'Config' foi removida, pois era da arquitetura antiga.
# A classe agora receberá a chave da API diretamente no seu construtor.

logger = logging.getLogger(__name__)

class OpenAILLMAdapter:
    def __init__(self, api_key: str):
        """
        Inicializa o cliente da OpenAI com a chave da API fornecida.
        """
        if not api_key:
            raise ValueError("A chave da API da OpenAI não foi fornecida.")
        self.client = OpenAI(api_key=api_key)
        logger.info("Adaptador da OpenAI inicializado com sucesso.")

    def get_completion(self, messages, model="gpt-4-turbo", temperature=0, max_tokens=2048, json_mode=False):
        """
        Obtém uma conclusão do modelo da OpenAI.
        """
        try:
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                params["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**params)
            
            content = response.choices[0].message.content
            return {"content": content}
        except Exception as e:
            logger.error(f"Erro ao chamar a API da OpenAI: {e}", exc_info=True)
            return {"error": str(e)}
