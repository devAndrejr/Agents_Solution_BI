import schedule
import time
import logging
import subprocess
import sys
import os

# Garante que o diretório de logs exista
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configuração de logging para o agente
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.FileHandler("logs/agente_atualizador.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

def run_export_script():
    """Executa o script de exportação de dados como um subprocesso."""
    logger.info("Disparando a execução do script de exportação de dados...")
    
    # Caminho para o script de exportação
    script_path = os.path.join("scripts", "export_sqlserver_to_parquet.py")
    
    try:
        # Executa o script usando o mesmo interpretador Python que executa o agente
        process = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8', errors='replace'
        )
        logger.info("Script de exportação executado com sucesso.")
        # Loga a saída padrão do script para referência
        if process.stdout:
            logger.info("Saída do script:\n%s", process.stdout)
        if process.stderr:
            logger.warning("Saída de erro (stderr) do script:\n%s", process.stderr)

    except subprocess.CalledProcessError as e:
        logger.error(f"O script de exportação falhou com código de saída {e.returncode}.")
        logger.error("Saída do script (stdout):\n%s", e.stdout)
        logger.error("Saída de erro (stderr):\n%s", e.stderr)
    except FileNotFoundError:
        logger.error(f"Erro: O script '{script_path}' não foi encontrado.")
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado ao executar o script de exportação: {e}")

# --- Agendamento ---
# Agendado para rodar duas vezes ao dia.
# Horários escolhidos: 10:00 e 22:00.
schedule.every().day.at("10:00").do(run_export_script)
schedule.every().day.at("22:00").do(run_export_script)

logger.info("Agente atualizador iniciado.")
logger.info("A exportação de dados está agendada para as 10:00 e 22:00.")

if __name__ == "__main__":
    # Executa uma vez ao iniciar para garantir que os dados estejam atualizados
    run_export_script() 
    while True:
        schedule.run_pending()
        time.sleep(60)
