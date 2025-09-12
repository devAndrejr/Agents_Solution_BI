import logging

from .base_agent import BaseAgent
from .prompt_loader import PromptLoader

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/agent.log",
    filemode="a",
)
logger = logging.getLogger("caculinha_dev_agent")


class CaculinhaDevAgent(BaseAgent):
    """Agente especializado em desenvolvimento de código estilo Vibe Coding."""

    def __init__(self, session_id=None, use_mock_data=False, mcp_adapter=None):
        """
        Inicializa o agente Caçulinha Dev.

        Args:
            session_id (str): ID da sessão para persistência de estado.
            use_mock_data (bool): Flag para usar dados mockados.
            mcp_adapter (object): Adaptador MCP para SQL Server.
        """
        super().__init__(session_id, use_mock_data, mcp_adapter)
        self._load_prompts()
        logger.info("Agente Caçulinha Dev inicializado. Sessão: %s", session_id)

    def _load_prompts(self):
        """Carrega os prompts do arquivo ou usa um fallback."""
        prompt_loader = PromptLoader()
        prompt_data = prompt_loader.load_prompt("prompt_caculinha_dev")

        if prompt_data:
            self.system_prompt = prompt_data.get("system_prompt", "")
            self.capabilities = prompt_data.get("capabilities", [])
            self.safety_rules = prompt_data.get("safety_rules", [])
            self.model_config = prompt_data.get("model_config", {})
            logger.info("Prompt carregado com sucesso para o agente Caçulinha Dev.")
        else:
            self.system_prompt = (
                "Você é o Caçulinha Dev, um assistente virtual "
                "especializado em desenvolvimento de código com estilo Vibe Coding."
            )
            self.capabilities = ["code_development", "code_review", "debugging"]
            self.safety_rules = ["no_malicious_code", "portuguese_only_responses"]
            self.model_config = {"model": "gpt-35-turbo", "temperature": 0.2}
            logger.warning("Usando prompt padrão para o agente Caçulinha Dev.")

    def process_query(self, query):
        """
        Processa uma consulta com foco em desenvolvimento de código.

        Args:
            query (str): A consulta do usuário.

        Returns:
            dict: Resposta processada.
        """
        logger.info("Agente Caçulinha Dev processando consulta: %s", query)

        if not self._is_relevant_query(query):
            logger.info("Consulta não relevante para o agente Dev: %s", query)
            return {
                "response": (
                    "Esta consulta pode ser melhor atendida por outro "
                    "agente especializado."
                ),
                "relevant": False,
            }

        try:
            result = super().process_query(query)

            if self._should_suggest_improvements(query):
                result["response"] += (
                    "\n\nPosso sugerir algumas melhorias para este código. "
                    "Gostaria de vê-las?"
                )
                result["can_improve"] = True

            return result
        except Exception as e:
            logger.error("Erro no agente Caçulinha Dev: %s", e)
            return {
                "response": "Desculpe, ocorreu um erro ao processar sua consulta.",
                "error": str(e),
            }

    def _is_relevant_query(self, query):
        """Verifica se a consulta é relevante para este agente."""
        query_lower = query.lower()
        keywords = [
            "código",
            "programação",
            "desenvolver",
            "implementar",
            "função",
            "classe",
            "método",
            "refatorar",
            "otimizar",
            "debug",
            "erro",
            "bug",
            "python",
            "javascript",
            "arquitetura",
            "padrão",
            "design pattern",
            "api",
            "interface",
            "módulo",
        ]
        return any(keyword in query_lower for keyword in keywords)

    def _should_suggest_improvements(self, query):
        """Verifica se deve sugerir melhorias de código."""
        query_lower = query.lower()
        improvement_keywords = [
            "revisar",
            "melhorar",
            "otimizar",
            "refatorar",
            "limpar",
            "performance",
            "desempenho",
            "legibilidade",
            "manutenção",
            "segurança",
        ]
        return any(keyword in query_lower for keyword in improvement_keywords)
