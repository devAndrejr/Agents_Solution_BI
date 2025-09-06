import logging
from typing import Any, Dict

from .mcp_manager import get_mcp_manager

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/mcp.log",
    filemode="a",
)
logger = logging.getLogger("mcp_query_adapter")


class MCPQueryAdapter:
    """Adaptador para integrar o MCP ao processador de consultas existente

    Esta classe serve como ponte entre o processador de consultas existente
    e o sistema MCP (Multi-Cloud Processing), permitindo que consultas sejam
    processadas em múltiplas nuvens de forma transparente.
    """

    def __init__(self):
        """Inicializa o adaptador MCP"""
        self.mcp_manager = get_mcp_manager()
        logger.info("MCPQueryAdapter inicializado")

    def process_query(
        self, query: str, use_distributed: bool = False
    ) -> Dict[str, Any]:
        """Processa uma consulta usando o MCP

        Args:
            query (str): A consulta a ser processada
            use_distributed (bool, optional): Se True, usa processamento distribuído
                em todos os provedores ativos. Default é False.

        Returns:
            Dict[str, Any]: Resultado do processamento da consulta
        """
        try:
            logger.info(f"Processando consulta via MCP: '{query}'")

            if use_distributed:
                result = self.mcp_manager.process_distributed(query)
            else:
                result = self.mcp_manager.process_query(query)

            # Adapta o resultado para o formato esperado pelo processador de consultas
            if result.get("success", False):
                # Extrai o resultado real da resposta do MCP
                mcp_result = result.get("result", {})
                if use_distributed:
                    # Combina resultados de múltiplos provedores
                    combined_data = self._combine_distributed_results(result)
                    return {
                        "type": "mcp_response",
                        "success": True,
                        "provider": "multiple",
                        "providers_used": result.get("successful_providers", 0),
                        "distributed": True,
                        "output": combined_data.get(
                            "output", "Processamento distribuído concluído"
                        ),
                        "data": combined_data.get("data", {}),
                    }
                else:
                    # Resultado de um único provedor
                    return {
                        "type": "mcp_response",
                        "success": True,
                        "provider": result.get("provider", "unknown"),
                        "distributed": False,
                        "output": mcp_result.get(
                            "result", "Consulta processada com sucesso"
                        ),
                        "data": mcp_result,
                    }
            else:
                # Retorna erro formatado
                return {
                    "type": "error",
                    "success": False,
                    "message": f"Erro no processamento MCP: {result.get('error', 'Erro desconhecido')}",
                }

        except Exception as e:
            logger.error(f"Erro ao processar consulta via MCP: {str(e)}")
            return {
                "type": "error",
                "success": False,
                "message": f"Erro ao processar consulta via MCP: {str(e)}",
            }

    def _combine_distributed_results(
        self, distributed_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combina resultados de processamento distribuído

        Args:
            distributed_result (Dict[str, Any]): Resultado do processamento distribuído

        Returns:
            Dict[str, Any]: Dados combinados dos vários provedores
        """
        results = distributed_result.get("results", [])
        if not results:
            return {"output": "Nenhum resultado disponível", "data": {}}

        # Combina os resultados de todos os provedores
        # Esta é uma implementação simples que pode ser expandida conforme necessário
        combined_output = f"Resultados de {len(results)} provedores:\n"
        combined_data = {}

        for idx, res in enumerate(results, 1):
            provider = res.get("provider", f"provedor-{idx}")
            result_data = res.get("result", {})
            result_text = result_data.get("result", "Sem resultado")

            combined_output += f"\n{idx}. {provider}: {result_text}"
            combined_data[provider] = result_data

        return {"output": combined_output, "data": combined_data}

    def get_active_providers(self) -> Dict[str, Any]:
        """Retorna informações sobre os provedores ativos

        Returns:
            Dict[str, Any]: Informações sobre os provedores ativos
        """
        return self.mcp_manager.get_provider_status()

    def is_mcp_available(self) -> bool:
        """Verifica se o MCP está disponível e configurado

        Returns:
            bool: True se o MCP está disponível, False caso contrário
        """
        status = self.mcp_manager.get_provider_status()
        return status.get("success", False) and status.get("active_count", 0) > 0


# Função auxiliar para obter uma instância do adaptador MCP
def get_mcp_adapter() -> MCPQueryAdapter:
    """Retorna uma instância do adaptador MCP

    Returns:
        MCPQueryAdapter: Instância do adaptador MCP
    """
    return MCPQueryAdapter()
