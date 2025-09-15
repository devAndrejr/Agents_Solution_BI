import os
import sys

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
print(f"Adicionado ao PYTHONPATH: {root_dir}")

# Importa as bibliotecas necessárias
import subprocess
import json
import time

# Configurações para o TestSprite
LOCAL_PORT = 8501  # Porta do Streamlit
PROJECT_PATH = root_dir
TEST_SCOPE = "codebase"  # Pode ser "codebase" ou "diff"

def run_testsprite():
    print("Iniciando o TestSprite para testes de frontend...")
    
    # Verifica se o servidor Streamlit está rodando
    try:
        import requests
        response = requests.get(f"http://localhost:{LOCAL_PORT}")
        if response.status_code != 200:
            print(f"Servidor Streamlit não está respondendo corretamente na porta {LOCAL_PORT}")
            print("Certifique-se de que o servidor Streamlit está rodando antes de executar este script")
            return False
    except Exception as e:
        print(f"Erro ao verificar o servidor Streamlit: {e}")
        print("Certifique-se de que o servidor Streamlit está rodando antes de executar este script")
        return False
    
    # Configuração do TestSprite
    testsprite_config = {
        "localPort": LOCAL_PORT,
        "type": "frontend",
        "projectPath": PROJECT_PATH,
        "testScope": TEST_SCOPE
    }
    
    print("Configuração do TestSprite:")
    print(json.dumps(testsprite_config, indent=2))
    
    print("\nPara executar o TestSprite, use o comando 'run_mcp' com os seguintes parâmetros:")
    print("server_name: mcp.config.usrlocalmcp.TestSprite")
    print("tool_name: testsprite_bootstrap_tests")
    print(f"args: {json.dumps(testsprite_config)}")
    
    return True

if __name__ == "__main__":
    run_testsprite()