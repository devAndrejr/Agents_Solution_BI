# run_app.py
import subprocess
import sys
import time
import logging
import webbrowser
import threading
from core.config.logging_config import setup_logging

# --- Constantes ---
FRONTEND_URL = "http://localhost:5173"
# Aumentado o delay para dar tempo aos servidores de dev, especialmente o Vite, de iniciar.
STARTUP_DELAY_SECONDS = 8

# Configuração do logging centralizado
setup_logging()

def open_browser():
    """Abre o navegador na URL do frontend."""
    logging.info(f"Abrindo o navegador em {FRONTEND_URL}...")
    try:
        webbrowser.open(FRONTEND_URL)
    except Exception as e:
        logging.error(f"Falha ao abrir o navegador: {e}")

def run_command(command, name, cwd=None, shell=False):
    """Executa um comando em um subprocesso e retorna o processo."""
    logging.info(f"Iniciando o processo '{name}': {' '.join(command)}")
    try:
        process = subprocess.Popen(command, cwd=cwd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        logging.info(f"Processo '{name}' iniciado com PID: {process.pid}. Aguardando inicialização...")
        return process
    except FileNotFoundError:
        logging.error(f"Comando não encontrado para o processo '{name}'. Verifique se o executável está no PATH.")
        return None
    except Exception as e:
        logging.error(f"Um erro inesperado ocorreu ao iniciar o processo '{name}': {e}")
        return None

def main():
    """Função principal para iniciar todos os serviços da aplicação."""
    logging.info("--- Iniciando Orquestrador da Aplicação Agent_BI ---")

    # Comandos para iniciar backend e frontend
    backend_command = [sys.executable, "-m", "uvicorn", "core.main:app", "--reload"]
    frontend_command = ["npm", "run", "dev"]

    # Inicia os processos
    backend_process = run_command(backend_command, "Backend FastAPI", shell=True)

    if not backend_process or not frontend_process:
        logging.error("Um ou mais processos falharam ao iniciar. Encerrando o orquestrador.")
        sys.exit(1)

    logging.info(f"Aguardando {STARTUP_DELAY_SECONDS} segundos para a inicialização dos serviços...")
    time.sleep(STARTUP_DELAY_SECONDS)

    # Verifica se os processos ainda estão ativos após o delay
    if backend_process.poll() is not None or frontend_process.poll() is not None:
        logging.error("Um dos processos encerrou inesperadamente durante a inicialização. Verifique os logs.")
        if backend_process.poll() is not None:
            logging.error(f"Logs do Backend (stderr):\n{backend_process.stderr.read()}")
        if frontend_process.poll() is not None:
            logging.error(f"Logs do Frontend (stderr):\n{frontend_process.stderr.read()}")
        sys.exit(1)

    logging.info("Aplicação iniciada com sucesso. Abrindo navegador...")
    open_browser()

    try:
        # Mantém o script principal rodando e monitorando
        while True:
            if backend_process.poll() is not None:
                logging.warning("O processo de backend foi encerrado inesperadamente.")
                break
            if frontend_process.poll() is not None:
                logging.warning("O processo de frontend foi encerrado inesperadamente.")
                break
            time.sleep(2)
    except KeyboardInterrupt:
        logging.info("Recebido sinal de interrupção (Ctrl+C). Encerrando processos...")
    finally:
        if backend_process.poll() is None:
            backend_process.terminate()
            logging.info("Processo de backend encerrado.")
        if frontend_process.poll() is None:
            frontend_process.terminate()
            logging.info("Processo de frontend encerrado.")
        logging.info("--- Orquestrador Finalizado ---")

if __name__ == "__main__":
    main()