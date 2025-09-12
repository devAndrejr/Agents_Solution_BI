import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict

# Importa os adaptadores MCP
try:
    from .context7_adapter import Context7MCPAdapter
    from .sqlserver_adapter import SQLServerMCPAdapter
except ImportError:
    # Fallback para importação direta (útil para testes)
    try:
        from context7_adapter import Context7MCPAdapter
        from sqlserver_adapter import SQLServerMCPAdapter
    except ImportError:
        pass

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/mcp.log",
    filemode="a",
)
logger = logging.getLogger("mcp_manager")


class MCPManager:
    """Gerenciador de Multi-Cloud Processing (MCP)

    Esta classe gerencia conexões e processamento distribuído em múltiplas nuvens,
    permitindo que consultas e análises de dados sejam processadas em paralelo
    em diferentes provedores de nuvem.
    """

    def __init__(self, config_file: str = None):
        """Inicializa o gerenciador MCP

        Args:
            config_file (str, optional): Caminho para o arquivo de configuração MCP.
                Se não fornecido, usa o padrão em data/mcp_config.json
        """
        self.providers = {}
        self.active_providers = []
        self.config_file = config_file or os.path.join(
            os.getcwd(), "data", "mcp_config.json"
        )
        self.load_config()
        logger.info(
            f"MCPManager inicializado com {len(self.active_providers)} provedores ativos"
        )

    def load_config(self) -> None:
        """Carrega a configuração do MCP do arquivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)

                self.providers = config.get("providers", {})
                self.active_providers = [
                    p
                    for p, details in self.providers.items()
                    if details.get("active", False)
                ]
                logger.info(
                    f"Configuração MCP carregada: {len(self.providers)} provedores configurados"
                )
            else:
                logger.warning(
                    f"Arquivo de configuração MCP não encontrado: {self.config_file}"
                )
                # Cria configuração padrão
                self._create_default_config()
        except Exception as e:
            logger.error(f"Erro ao carregar configuração MCP: {str(e)}")
            self.providers = {}
            self.active_providers = []

    def _create_default_config(self) -> None:
        """Cria um arquivo de configuração padrão se não existir"""
        default_config = {
            "providers": {
                "aws": {
                    "name": "Amazon Web Services",
                    "active": False,
                    "credentials": {
                        "access_key": "",
                        "secret_key": "",
                        "region": "us-east-1",
                    },
                    "services": {"lambda": True, "s3": True, "dynamodb": False},
                },
                "azure": {
                    "name": "Microsoft Azure",
                    "active": False,
                    "credentials": {
                        "connection_string": "",
                        "tenant_id": "",
                        "client_id": "",
                        "client_secret": "",
                    },
                    "services": {
                        "functions": True,
                        "blob_storage": True,
                        "cosmos_db": False,
                    },
                },
                "gcp": {
                    "name": "Google Cloud Platform",
                    "active": False,
                    "credentials": {"project_id": "", "service_account_key": ""},
                    "services": {
                        "cloud_functions": True,
                        "cloud_storage": True,
                        "bigquery": False,
                    },
                },
                "context7": {
                    "name": "Context7 Documentation",
                    "active": False,
                    "credentials": {
                        "api_key": "",
                        "base_url": "https://api.context7.com",
                    },
                    "services": {
                        "documentation": True,
                        "library_resolution": True,
                    },
                },
            },
            "settings": {
                "default_provider": "",
                "fallback_provider": "",
                "timeout": 30,
                "max_retries": 3,
                "parallel_execution": True,
                "load_balancing": "round-robin",  # round-robin, weighted, auto
            },
        }

        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(default_config, f, indent=4)
            logger.info(
                f"Arquivo de configuração MCP padrão criado: {self.config_file}"
            )
            self.providers = default_config.get("providers", {})
        except Exception as e:
            logger.error(f"Erro ao criar configuração MCP padrão: {str(e)}")

    def save_config(self) -> bool:
        """Salva a configuração atual no arquivo JSON

        Returns:
            bool: True se a configuração foi salva com sucesso, False caso contrário
        """
        try:
            config = {
                "providers": self.providers,
                "settings": {
                    "default_provider": self.get_default_provider(),
                    "fallback_provider": self.get_fallback_provider(),
                    "timeout": 30,
                    "max_retries": 3,
                    "parallel_execution": True,
                    "load_balancing": "round-robin",
                },
            }

            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
            logger.info(f"Configuração MCP salva em: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração MCP: {str(e)}")
            return False

    def get_default_provider(self) -> str:
        """Retorna o provedor padrão configurado

        Returns:
            str: Nome do provedor padrão ou string vazia se não configurado
        """
        for provider, details in self.providers.items():
            if details.get("default", False) and details.get("active", False):
                return provider
        return self.active_providers[0] if self.active_providers else ""

    def get_fallback_provider(self) -> str:
        """Retorna o provedor de fallback configurado

        Returns:
            str: Nome do provedor de fallback ou string vazia se não configurado
        """
        for provider, details in self.providers.items():
            if details.get("fallback", False) and details.get("active", False):
                return provider
        return ""

    def add_provider(self, provider_id: str, config: Dict[str, Any]) -> bool:
        """Adiciona um novo provedor de nuvem

        Args:
            provider_id (str): Identificador único do provedor
            config (Dict[str, Any]): Configuração do provedor

        Returns:
            bool: True se o provedor foi adicionado com sucesso, False caso contrário
        """
        try:
            if provider_id in self.providers:
                logger.warning(f"Provedor {provider_id} já existe e será sobrescrito")

            self.providers[provider_id] = config
            if config.get("active", False):
                self.active_providers.append(provider_id)

            self.save_config()
            logger.info(f"Provedor {provider_id} adicionado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar provedor {provider_id}: {str(e)}")
            return False

    def remove_provider(self, provider_id: str) -> bool:
        """Remove um provedor de nuvem

        Args:
            provider_id (str): Identificador único do provedor

        Returns:
            bool: True se o provedor foi removido com sucesso, False caso contrário
        """
        try:
            if provider_id not in self.providers:
                logger.warning(f"Provedor {provider_id} não encontrado")
                return False

            del self.providers[provider_id]
            if provider_id in self.active_providers:
                self.active_providers.remove(provider_id)

            self.save_config()
            logger.info(f"Provedor {provider_id} removido com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover provedor {provider_id}: {str(e)}")
            return False

    def activate_provider(self, provider_id: str) -> bool:
        """Ativa um provedor de nuvem

        Args:
            provider_id (str): Identificador único do provedor

        Returns:
            bool: True se o provedor foi ativado com sucesso, False caso contrário
        """
        try:
            if provider_id not in self.providers:
                logger.warning(f"Provedor {provider_id} não encontrado")
                return False

            self.providers[provider_id]["active"] = True
            if provider_id not in self.active_providers:
                self.active_providers.append(provider_id)

            self.save_config()
            logger.info(f"Provedor {provider_id} ativado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao ativar provedor {provider_id}: {str(e)}")
            return False

    def deactivate_provider(self, provider_id: str) -> bool:
        """Desativa um provedor de nuvem

        Args:
            provider_id (str): Identificador único do provedor

        Returns:
            bool: True se o provedor foi desativado com sucesso, False caso contrário
        """
        try:
            if provider_id not in self.providers:
                logger.warning(f"Provedor {provider_id} não encontrado")
                return False

            self.providers[provider_id]["active"] = False
            if provider_id in self.active_providers:
                self.active_providers.remove(provider_id)

            self.save_config()
            logger.info(f"Provedor {provider_id} desativado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao desativar provedor {provider_id}: {str(e)}")
            return False

    def process_query(self, query: str, provider_id: str = None) -> Dict[str, Any]:
        """Processa uma consulta usando o provedor especificado ou o padrão

        Args:
            query (str): A consulta a ser processada
            provider_id (str, optional): Identificador do provedor a ser usado.
                Se None, usa o provedor padrão.

        Returns:
            Dict[str, Any]: Resultado do processamento da consulta
        """
        if not self.active_providers:
            logger.warning("Nenhum provedor ativo disponível para processar a consulta")
            return {
                "success": False,
                "error": "Nenhum provedor ativo disponível",
                "result": None,
            }

        # Se não especificado, usa o provedor padrão
        if not provider_id:
            provider_id = self.get_default_provider()

        # Se o provedor especificado não estiver ativo, usa o padrão
        if provider_id not in self.active_providers:
            logger.warning(
                f"Provedor {provider_id} não está ativo. Usando provedor padrão."
            )
            provider_id = self.get_default_provider()

        try:
            # Verifica se é uma consulta para SQL Server
            if provider_id == "sqlserver":
                try:
                    # Inicializa o adaptador SQL Server
                    adapter = SQLServerMCPAdapter()
                    if adapter.is_available:
                        # Processa a consulta usando o adaptador SQL Server
                        result = adapter.process_query(query)
                        return {
                            "success": True,
                            "provider": "sqlserver",
                            "result": result,
                        }
                    else:
                        logger.warning(
                            "Adaptador SQL Server não está disponível. Usando processamento padrão."
                        )
                except Exception as e:
                    logger.error(
                        f"Erro ao processar consulta via adaptador SQL Server: {str(e)}"
                    )

            # Verifica se é uma consulta para Context7
            elif provider_id == "context7":
                try:
                    # Inicializa o adaptador Context7
                    adapter = Context7MCPAdapter()
                    if adapter.is_available:
                        # Processa a consulta usando o adaptador Context7
                        result = adapter.process_query(query)
                        return {
                            "success": True,
                            "provider": "context7",
                            "result": result,
                        }
                    else:
                        logger.warning(
                            "Adaptador Context7 não está disponível. Usando processamento padrão."
                        )
                except Exception as e:
                    logger.error(
                        f"Erro ao processar consulta via adaptador Context7: {str(e)}"
                    )

            # Para outros provedores ou fallback, usa o processamento padrão
            logger.info(f"Processando consulta usando provedor padrão: {provider_id}")

            # Simulação de processamento para provedores não implementados
            result = {
                "provider": provider_id,
                "query": query,
                "processed": True,
                "timestamp": "2023-04-15T10:30:00Z",
                "result": f"Resultado simulado para: {query}",
            }

            return {"success": True, "provider": provider_id, "result": result}
        except Exception as e:
            logger.error(
                f"Erro ao processar consulta com provedor {provider_id}: {str(e)}"
            )

            # Tenta com o provedor de fallback se disponível
            fallback = self.get_fallback_provider()
            if fallback and fallback != provider_id:
                logger.info(f"Tentando processar com provedor de fallback: {fallback}")
                try:
                    # Implementação do fallback
                    result = {
                        "provider": fallback,
                        "query": query,
                        "processed": True,
                        "timestamp": "2023-04-15T10:30:00Z",
                        "result": f"Resultado de fallback para: {query}",
                    }

                    return {
                        "success": True,
                        "provider": fallback,
                        "fallback_used": True,
                        "result": result,
                    }
                except Exception as fallback_error:
                    logger.error(
                        f"Erro no provedor de fallback {fallback}: {str(fallback_error)}"
                    )

            return {"success": False, "error": str(e), "result": None}

    def process_distributed(self, query: str) -> Dict[str, Any]:
        """Processa uma consulta de forma distribuída em todos os provedores ativos

        Args:
            query (str): A consulta a ser processada

        Returns:
            Dict[str, Any]: Resultados combinados do processamento da consulta
        """
        if not self.active_providers:
            logger.warning(
                "Nenhum provedor ativo disponível para processamento distribuído"
            )
            return {
                "success": False,
                "error": "Nenhum provedor ativo disponível",
                "results": [],
            }

        # Inicializa adaptadores específicos se disponíveis
        adapters = {}

        # Verifica se o SQL Server está entre os provedores ativos
        if "sqlserver" in self.active_providers:
            try:
                sqlserver_adapter = SQLServerMCPAdapter()
                if sqlserver_adapter.is_available:
                    adapters["sqlserver"] = sqlserver_adapter
            except Exception as e:
                logger.error(f"Erro ao inicializar adaptador SQL Server: {str(e)}")

        # Verifica se o Context7 está entre os provedores ativos
        if "context7" in self.active_providers:
            try:
                context7_adapter = Context7MCPAdapter()
                if context7_adapter.is_available:
                    adapters["context7"] = context7_adapter
            except Exception as e:
                logger.error(f"Erro ao inicializar adaptador Context7: {str(e)}")

        results = []
        errors = []

        # Função para processar em um provedor específico
        def process_in_provider(provider):
            try:
                result = self.process_query(query, provider)
                return result
            except Exception as e:
                logger.error(
                    f"Erro no processamento distribuído com {provider}: {str(e)}"
                )
                return {"success": False, "provider": provider, "error": str(e)}

        # Executa em paralelo em todos os provedores ativos
        with ThreadPoolExecutor(max_workers=len(self.active_providers)) as executor:
            futures = {
                executor.submit(process_in_provider, provider): provider
                for provider in self.active_providers
            }

            for future in futures:
                provider = futures[future]
                try:
                    result = future.result()
                    if result["success"]:
                        results.append(result)
                    else:
                        errors.append(
                            {
                                "provider": provider,
                                "error": result.get("error", "Erro desconhecido"),
                            }
                        )
                except Exception as e:
                    errors.append({"provider": provider, "error": str(e)})

        # Combina os resultados
        combined_result = {
            "success": len(results) > 0,
            "total_providers": len(self.active_providers),
            "successful_providers": len(results),
            "failed_providers": len(errors),
            "results": results,
            "errors": errors,
        }

        return combined_result

    def get_provider_status(self, provider_id: str = None) -> Dict[str, Any]:
        """Verifica o status de um provedor específico ou de todos os provedores

        Args:
            provider_id (str, optional): Identificador do provedor. Se None, verifica todos.

        Returns:
            Dict[str, Any]: Status do(s) provedor(es)
        """
        if provider_id:
            if provider_id not in self.providers:
                return {
                    "success": False,
                    "error": f"Provedor {provider_id} não encontrado",
                }

            provider_info = self.providers[provider_id]
            is_active = provider_id in self.active_providers

            # Aqui implementaria verificação real de conectividade
            # Por enquanto, apenas retorna as informações básicas
            return {
                "success": True,
                "provider": provider_id,
                "name": provider_info.get("name", provider_id),
                "active": is_active,
                "services": provider_info.get("services", {}),
                "is_default": self.get_default_provider() == provider_id,
                "is_fallback": self.get_fallback_provider() == provider_id,
            }
        else:
            # Retorna status de todos os provedores
            all_status = []
            for pid in self.providers:
                status = self.get_provider_status(pid)
                if status["success"]:
                    all_status.append(status)

            return {
                "success": True,
                "providers": all_status,
                "active_count": len(self.active_providers),
                "total_count": len(self.providers),
            }


# Função auxiliar para obter uma instância do gerenciador MCP
def get_mcp_manager(config_file: str = None) -> MCPManager:
    """Retorna uma instância do gerenciador MCP

    Args:
        config_file (str, optional): Caminho para o arquivo de configuração MCP.
            Se não fornecido, usa o padrão.

    Returns:
        MCPManager: Instância do gerenciador MCP
    """
    return MCPManager(config_file)
