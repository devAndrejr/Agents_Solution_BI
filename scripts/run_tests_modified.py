import os
import subprocess
import sys
import time

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
print(f"Adicionado ao PYTHONPATH: {root_dir}")

import requests

# Agora podemos importar módulos do projeto
try:
    from core.utils.env_setup import setup_environment
    setup_environment()
    print("Ambiente configurado com sucesso.")
except ImportError as e:
    print(f"Erro ao importar: {e}")
    # Continua mesmo com erro de importação

SERVER_CMD = [sys.executable, "-m", "core.api.run_api"]
SERVER_URL = "http://localhost:5000/api/status"
PYTEST_CMD = [sys.executable, "-m", "pytest", "-v", "--maxfail=3", "--tb=short"]


def wait_for_server(url, timeout=30):
    print(f"Aguardando o servidor ficar disponível em {url}...")
    for _ in range(timeout):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                print("Servidor disponível!")
                return True
        except Exception as e:
            print(f"Aguardando servidor... ({e.__class__.__name__})")
        time.sleep(1)
    print("Timeout ao aguardar o servidor.")
    return False


def main():
    # Inicia o servidor Flask
    print("Iniciando o servidor Flask...")
    server_proc = subprocess.Popen(
        SERVER_CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    try:
        if not wait_for_server(SERVER_URL, timeout=30):
            print("Não foi possível iniciar o servidor Flask.")
            server_proc.terminate()
            sys.exit(1)

        # Executa o pytest
        print("Executando os testes...")
        result = subprocess.run(PYTEST_CMD)
        exit_code = result.returncode
    finally:
        print("Encerrando o servidor Flask...")
        server_proc.terminate()
        try:
            server_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server_proc.kill()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()