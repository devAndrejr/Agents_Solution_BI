# Módulo MCP (Multi-Cloud Processing)
# Este módulo gerencia conexões e processamento distribuído em múltiplas nuvens

# Importação explícita para garantir que a função esteja disponível
from .sqlserver_adapter import SQLServerMCPAdapter, get_sqlserver_mcp_adapter

# Definição explícita do que é exportado pelo módulo
__all__ = ["SQLServerMCPAdapter", "get_sqlserver_mcp_adapter"]
