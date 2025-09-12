#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Adaptador MCP para SQL Server

Este módulo implementa a interface AdaptadorMCPInterface para o SQL Server,
permitindo a integração padronizada com o serviço MCP.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

# Importar a interface
try:
    from analise.interfaces.adaptador_mcp_interface import \
        AdaptadorMCPInterface
except ImportError:
    # Fallback para importação relativa se o módulo não estiver no path
    try:
        from ...analise.interfaces.adaptador_mcp_interface import \
            AdaptadorMCPInterface
    except ImportError:
        # Definir uma classe base vazia para não quebrar a herança
        class AdaptadorMCPInterface:
            pass


# Importar o adaptador SQL Server existente
try:
    from core.mcp.sqlserver_adapter import \
        SQLServerMCPAdapter as OriginalSQLServerMCPAdapter
except ImportError:
    # Fallback para importação relativa
    try:
        from .sqlserver_adapter import \
            SQLServerMCPAdapter as OriginalSQLServerMCPAdapter
    except ImportError:
        # Definir uma classe mock para não quebrar a execução
        class OriginalSQLServerMCPAdapter:
            def __init__(self, config_file=None):
                self.is_available = False
                self.config = {}

            def process_query(self, query):
                return {"error": "SQLServerMCPAdapter não disponível"}

            def _check_availability(self):
                return False

            def _get_connection(self):
                return None


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/mcp_sqlserver_adapter.log",
    filemode="a",
)
logger = logging.getLogger("sqlserver_mcp_adapter")


class SQLServerMCPAdapter(AdaptadorMCPInterface):
    """Adaptador MCP para SQL Server que implementa a interface AdaptadorMCPInterface

    Esta classe atua como um wrapper para o SQLServerMCPAdapter existente,
    adaptando-o para a interface padrão AdaptadorMCPInterface.
    """

    def __init__(self, config_file: str = None):
        """
        Inicializa o adaptador MCP para SQL Server

        Args:
            config_file (str, optional): Caminho para o arquivo de configuração.
                Se não fornecido, usa o padrão em data/sqlserver_mcp_config.json
                ou as credenciais diretamente do arquivo .env
        """
        # Inicializa o adaptador SQL Server existente
        self.adapter = OriginalSQLServerMCPAdapter(config_file)
        self.is_available = self.adapter.is_available

        # Registra informações sobre a inicialização
        logger.info(
            f"SQLServerMCPAdapter inicializado com interface AdaptadorMCPInterface"
        )
        logger.info(f"Status de disponibilidade: {self.is_available}")

    def conectar(self, configuracao: Dict[str, Any]) -> bool:
        """Implementação do método da interface AdaptadorMCPInterface

        Args:
            configuracao (Dict[str, Any]): Parâmetros de configuração para conexão

        Returns:
            bool: True se a conexão foi estabelecida com sucesso, False caso contrário
        """
        try:
            # Atualiza a configuração do adaptador existente
            if configuracao:
                self.adapter.config.update(configuracao)

            # Tenta estabelecer uma conexão
            connection = self.adapter._get_connection()
            if connection:
                connection.close()
                self.is_available = True
                logger.info("Conexão estabelecida com sucesso")
                return True
            else:
                self.is_available = False
                logger.warning("Não foi possível estabelecer conexão")
                return False
        except Exception as e:
            logger.error(f"Erro ao conectar ao serviço MCP: {e}")
            self.is_available = False
            return False

    def obter_contexto(
        self, consulta: str, parametros: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Implementação do método da interface AdaptadorMCPInterface

        Args:
            consulta (str): Consulta para a qual o contexto é necessário
            parametros (Optional[Dict[str, Any]], optional): Parâmetros adicionais. Defaults to None.

        Returns:
            Dict[str, Any]: Contexto obtido do serviço MCP
        """
        try:
            # Utiliza o método process_query do adaptador existente
            resultado = self.adapter.process_query(consulta)

            # Verifica se houve erro
            if "error" in resultado:
                logger.error(f"Erro ao processar consulta: {resultado['error']}")
                return {
                    "status": "error",
                    "mensagem": resultado["error"],
                    "dados": None,
                }

            # Retorna o resultado formatado
            return {
                "status": "success",
                "mensagem": "Contexto obtido com sucesso",
                "dados": resultado,
            }
        except Exception as e:
            logger.error(f"Erro ao obter contexto: {e}")
            return {"status": "error", "mensagem": str(e), "dados": None}

    def processar_resultado(self, resultado: Dict[str, Any]) -> Dict[str, Any]:
        """Implementação do método da interface AdaptadorMCPInterface

        Args:
            resultado (Dict[str, Any]): Resultado bruto do serviço MCP

        Returns:
            Dict[str, Any]: Resultado processado e formatado
        """
        # Processa o resultado para um formato padronizado
        try:
            if not resultado or "error" in resultado:
                return {
                    "status": "error",
                    "mensagem": resultado.get("error", "Erro desconhecido"),
                    "dados": None,
                }

            # Formata o resultado para o padrão esperado
            return {
                "status": "success",
                "mensagem": "Resultado processado com sucesso",
                "dados": resultado,
            }
        except Exception as e:
            logger.error(f"Erro ao processar resultado: {e}")
            return {"status": "error", "mensagem": str(e), "dados": None}

    def verificar_status(self) -> Dict[str, Any]:
        """Implementação do método da interface AdaptadorMCPInterface

        Returns:
            Dict[str, Any]: Informações sobre o status da conexão
        """
        # Atualiza o status de disponibilidade
        self.is_available = self.adapter._check_availability()

        return {
            "disponivel": self.is_available,
            "ultima_verificacao": datetime.now().isoformat(),
            "servidor": self.adapter.config.get("connection", {}).get("server", "N/A"),
            "banco_dados": self.adapter.config.get("connection", {}).get(
                "database", "N/A"
            ),
            "timeout": self.adapter.config.get("processing", {}).get("timeout", 30),
        }

    def desconectar(self) -> bool:
        """Implementação do método da interface AdaptadorMCPInterface

        Returns:
            bool: True se a desconexão foi realizada com sucesso, False caso contrário
        """
        try:
            # Como o adaptador SQL Server não mantém uma conexão persistente,
            # apenas registramos a operação
            logger.info("Desconectando do serviço SQL Server MCP")
            self.is_available = False
            return True
        except Exception as e:
            logger.error(f"Erro ao desconectar: {e}")
            return False
