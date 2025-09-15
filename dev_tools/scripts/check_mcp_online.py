# import os  # Remove this line if present
import sys

from core.tools.node_mcp_client import get_node_mcp_client


def check_mcp_online():
    """Check if MCP is online and responding."""
    client = get_node_mcp_client()
    if client is None:
        print("Não foi possível obter o cliente MCP. " "Verifique a configuração.")
        return False
    try:
        resp = client.list_resources()
        if resp.get("success"):
            print("MCP online e respondendo.")
            return True
        else:
            print(f"MCP respondeu, mas sem sucesso: {resp}")
            return False
    except (AttributeError, ConnectionError, OSError) as e:
        print(f"Erro ao conectar ao MCP: {e}")
        return False


if __name__ == "__main__":
    ok = check_mcp_online()
    sys.exit(0 if ok else 1)
