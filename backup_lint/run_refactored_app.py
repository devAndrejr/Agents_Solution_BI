# run_refactored_app.py
from core.config.settings import settings
from core.connectivity.sql_server_adapter import SQLServerAdapter
from core.orchestration.supervisor import Supervisor

def main():
    """
    Composition Root: Where all dependencies are created and injected.
    """
    # 1. A configuração é carregada a partir da instância única
    app_settings = settings

    # 2. O adaptador de banco de dados (Strategy) é escolhido e instanciado
    db_adapter = SQLServerAdapter(settings=app_settings)

    # 3. O Supervisor é criado, recebendo suas dependências prontas
    supervisor = Supervisor(settings=app_settings, db_adapter=db_adapter)

    # 4. A aplicação é executada
    supervisor.run_task("Gere um relatório de vendas para o último trimestre.")

if __name__ == "__main__":
    main()