# core/orchestration/supervisor.py
from core.config.settings import Settings
from core.connectivity.base import DatabaseAdapter
# Importar outros agentes necessários
# from core.agents.code_gen_agent import CodeGenAgent

class Supervisor:
    def __init__(self, settings: Settings, db_adapter: DatabaseAdapter):
        """
        Initializes the Supervisor with its dependencies (Dependency Injection).
        """
        self.settings = settings
        self.db_adapter = db_adapter
        # self.code_agent = CodeGenAgent(llm_config=self.settings.LLM_MODEL_NAME)
        print("Supervisor initialized with a decoupled database adapter.")

    def run_task(self, user_query: str):
        """
        Example task execution flow.
        """
        print(f"Running task for query: '{user_query}'")
        
        # 1. Conectar ao banco de forma desacoplada
        self.db_adapter.connect()
        
        # 2. Usar o adaptador para obter dados
        schema = self.db_adapter.get_schema()
        print("Database schema retrieved:", schema)
        
        # 3. Orquestrar outros agentes, passando o contexto necessário
        # generated_code = self.code_agent.generate(user_query, schema)
        
        # 4. Desconectar
        self.db_adapter.disconnect()
        
        return "Task completed successfully."