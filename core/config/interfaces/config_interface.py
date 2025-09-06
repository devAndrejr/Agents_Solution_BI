#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interface para Configuração Centralizada

Este módulo define interfaces abstratas para padronizar o acesso
às configurações do sistema de forma centralizada.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ConfigInterface(ABC):
    """Interface abstrata para acesso às configurações"""

    @abstractmethod
    def carregar_configuracoes(self, caminho: Optional[str] = None) -> bool:
        """Carrega as configurações do sistema

        Args:
            caminho (Optional[str], optional): Caminho para o arquivo de configuração. Defaults to None.

        Returns:
            bool: True se as configurações foram carregadas com sucesso, False caso contrário
        """

    @abstractmethod
    def obter_configuracao(self, chave: str, padrao: Any = None) -> Any:
        """Obtém o valor de uma configuração

        Args:
            chave (str): Chave da configuração
            padrao (Any, optional): Valor padrão caso a configuração não exista. Defaults to None.

        Returns:
            Any: Valor da configuração ou o valor padrão
        """

    @abstractmethod
    def definir_configuracao(self, chave: str, valor: Any) -> bool:
        """Define o valor de uma configuração

        Args:
            chave (str): Chave da configuração
            valor (Any): Valor a ser definido

        Returns:
            bool: True se a configuração foi definida com sucesso, False caso contrário
        """

    @abstractmethod
    def salvar_configuracoes(self, caminho: Optional[str] = None) -> bool:
        """Salva as configurações do sistema

        Args:
            caminho (Optional[str], optional): Caminho para salvar o arquivo de configuração. Defaults to None.

        Returns:
            bool: True se as configurações foram salvas com sucesso, False caso contrário
        """

    @abstractmethod
    def validar_configuracoes(self) -> Dict[str, List[str]]:
        """Valida as configurações do sistema

        Returns:
            Dict[str, List[str]]: Dicionário com chaves de configurações inválidas e mensagens de erro
        """

    @abstractmethod
    def obter_configuracao_segura(self, chave: str, padrao: Any = None) -> Any:
        """Obtém o valor de uma configuração sensível de forma segura

        Args:
            chave (str): Chave da configuração sensível
            padrao (Any, optional): Valor padrão caso a configuração não exista. Defaults to None.

        Returns:
            Any: Valor da configuração sensível ou o valor padrão
        """
