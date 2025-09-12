#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interface para Adaptadores MCP

Este módulo define interfaces abstratas para padronizar a comunicação
com serviços externos através de adaptadores MCP.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class MCPAdapterInterface(ABC):
    """Interface abstrata para adaptadores MCP"""

    @abstractmethod
    def conectar(self) -> bool:
        """Estabelece conexão com o serviço externo

        Returns:
            bool: True se a conexão foi estabelecida com sucesso, False caso contrário
        """

    @abstractmethod
    def desconectar(self) -> bool:
        """Encerra a conexão com o serviço externo

        Returns:
            bool: True se a conexão foi encerrada com sucesso, False caso contrário
        """

    @abstractmethod
    def executar_comando(
        self, comando: str, parametros: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executa um comando no serviço externo

        Args:
            comando (str): Comando a ser executado
            parametros (Optional[Dict[str, Any]], optional): Parâmetros para o comando. Defaults to None.

        Returns:
            Dict[str, Any]: Resultado da execução do comando
        """

    @abstractmethod
    def verificar_status(self) -> Dict[str, Any]:
        """Verifica o status da conexão com o serviço externo

        Returns:
            Dict[str, Any]: Informações sobre o status da conexão
        """

    @abstractmethod
    def tratar_erro(self, erro: Any) -> Dict[str, Any]:
        """Trata erros de comunicação com o serviço externo

        Args:
            erro (Any): Erro ocorrido durante a comunicação

        Returns:
            Dict[str, Any]: Informações sobre o erro tratado
        """

    @abstractmethod
    def executar_fallback(
        self, comando: str, parametros: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executa uma operação alternativa em caso de falha na comunicação principal

        Args:
            comando (str): Comando que falhou
            parametros (Optional[Dict[str, Any]], optional): Parâmetros do comando. Defaults to None.

        Returns:
            Dict[str, Any]: Resultado da operação de fallback
        """
