import os
from core.llm_adapter import OpenAILLMAdapter
from core.config.config import Config # Importar Config para garantir que as variáveis de ambiente sejam carregadas

# Garante que as variáveis de ambiente sejam carregadas
_ = Config()

llm_adapter = OpenAILLMAdapter()

try:
    response = llm_adapter.get_completion(messages=[{"role": "user", "content": "Hello"}])
    if "error" in response:
        print(f"Erro na conexão com OpenAI: {response['error']}")
    else:
        print(f"Conexão com OpenAI bem-sucedida! Resposta: {response['content'][:50]}...")
except Exception as e:
    print(f"Erro inesperado na conexão com OpenAI: {e}")