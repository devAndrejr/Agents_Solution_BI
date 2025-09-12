#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fábrica de Componentes

Este módulo implementa o padrão Factory para criar e gerenciar instâncias
dos diversos componentes do sistema, facilitando a integração entre eles
e reduzindo o acoplamento.
"""

import logging
from functools import wraps  # Movido para o nível do módulo
from typing import Any, Dict, Optional

# Importa outros componentes conforme necessário
try:
    from core.mcp.context7_adapter import Context7MCPAdapter
    from core.mcp.sqlserver_adapter import SQLServerMCPAdapter

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

try:
    from core.agents.product_agent import ProductAgent

    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

# --- Lógica do Servidor Web (deveria ser movida para um módulo próprio) ---
try:
    from flask import (Flask, redirect, render_template, request, session,
                       url_for)

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class WebServer:
    def __init__(self, host="127.0.0.1", port=5000):
        if not FLASK_AVAILABLE:
            raise ImportError(
                "Flask não está instalado. Instale com 'pip install flask'."
            )
        self.host = host
        self.port = port
        import os

        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.app = Flask(
            "server",
            template_folder=os.path.join(base_dir, "web", "templates"),
            static_folder=os.path.join(base_dir, "web", "static"),
        )
        self.app.config["DEBUG"] = True
        self.app.config["SECRET_KEY"] = os.getenv(
            "SECRET_KEY", "chave_secreta_component_factory"
        )  # Adicionado
        self._running = False

        # Placeholder para usuários (similar ao servidor_integrado.py)
        self.USERS = {
            "admin": {"password": "admin123", "name": "Administrador CF"},
            "usuario": {"password": "senha123", "name": "Usuário Padrão CF"},
        }

        self._setup_routes()

    # Decorator para verificar se o usuário está logado (Adicionado)
    def _login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "username" not in session:
                return redirect(
                    url_for("login_route")
                )  # Aponta para a nova rota de login
            return f(*args, **kwargs)

        return decorated_function

    def _setup_routes(self):
        @self.app.route("/")
        @self._login_required  # Adicionado decorador
        def index():
            # Passa o nome do usuário para o template, se logado
            return render_template("index.html", username=session.get("name", ""))

        # Rota de login (Adicionado)
        @self.app.route("/login", methods=["GET", "POST"])
        def login_route():  # Nome da função alterado para evitar conflito
            error = None
            if request.method == "POST":
                username = request.form.get("username")
                password = request.form.get("password")
                if (
                    username in self.USERS
                    and self.USERS[username]["password"] == password
                ):
                    session["username"] = username
                    session["name"] = self.USERS[username]["name"]
                    logging.getLogger("WebServer").info(
                        f"Login bem-sucedido para o usuário: {username} via ComponentFactory"
                    )
                    return redirect(url_for("index"))
                else:
                    error = "Usuário ou senha incorretos"
                    logging.getLogger("WebServer").warning(
                        f"Tentativa de login falhou para o usuário: {username} via ComponentFactory"
                    )
            return render_template("login.html", error=error)

        # Rota de logout (Adicionado)
        @self.app.route("/logout")
        def logout_route():  # Nome da função alterado para evitar conflito
            session.pop("username", None)
            session.pop("name", None)
            logging.getLogger("WebServer").info(
                "Usuário deslogado via ComponentFactory"
            )
            return redirect(url_for("login_route"))

        # Registra as rotas da API
        try:
            from core.api import register_routes

            register_routes(self.app)
            import logging

            logging.getLogger("WebServer").info("Rotas da API registradas com sucesso")
        except Exception as e:
            import logging

            logging.getLogger("WebServer").error(f"Erro ao registrar rotas da API: {e}")

    def run(self, host=None, port=None, **kwargs):
        """Inicia o servidor Flask de forma síncrona (compatível com Flask)

        Args:
            host (str, optional): Host para o servidor. Defaults to None.
            port (int, optional): Porta para o servidor. Defaults to None.
            **kwargs: Parâmetros adicionais são ignorados para compatibilidade

        Returns:
            bool: True se o servidor foi iniciado com sucesso
        """
        try:
            # Atualiza host e port se fornecidos
            host = host or self.host
            port = port or self.port

            # Configura o status de execução
            self._running = True

            # Notifica o EventManager que o servidor está iniciando
            from core.utils.event_manager import EventManager

            EventManager.notify("web.server.started", {"port": port, "host": host})

            # Inicia o servidor Flask (esta chamada é bloqueante)
            self.app.run(
                host=host, port=port, debug=True, use_reloader=True
            )  # Alterado para use_reloader=True

            return True
        except Exception as e:
            import logging

            logging.getLogger("WebServer").error(f"Erro ao iniciar o servidor web: {e}")
            self._running = False
            return False


# --- FIM: WebServer ---


class ComponentFactory:
    """Fábrica para criar e gerenciar componentes do sistema"""

    # Dicionário para armazenar as instâncias dos componentes (Singleton)
    _components: Dict[str, Any] = {}

    # Logger
    logger = logging.getLogger("ComponentFactory")

    @classmethod
    def get_mcp_adapter(cls, adapter_type: str = "sqlserver") -> Optional[Any]:
        """Obtém uma instância do adaptador MCP

        Args:
            adapter_type (str, optional): Tipo de adaptador MCP. Defaults to 'sqlserver'.

        Returns:
            Optional[Any]: Instância do adaptador MCP ou None se não disponível
        """
        if not MCP_AVAILABLE:
            cls.logger.warning("Componentes MCP não estão disponíveis")
            return None

        adapter_key = f"mcp_{adapter_type}"

        if adapter_key not in cls._components:
            cls.logger.info(f"Criando nova instância do adaptador MCP: {adapter_type}")

            if adapter_type == "sqlserver":
                cls._components[adapter_key] = SQLServerMCPAdapter()
            elif adapter_type == "context7":
                cls._components[adapter_key] = Context7MCPAdapter()
            else:
                cls.logger.error(f"Tipo de adaptador MCP desconhecido: {adapter_type}")
                return None

        return cls._components[adapter_key]

    @classmethod
    def get_product_agent(cls) -> Optional[Any]:
        """Obtém uma instância do agente de produtos

        Returns:
            Optional[Any]: Instância do agente de produtos ou None se não disponível
        """
        if not AGENTS_AVAILABLE:
            cls.logger.warning("Componentes de agentes não estão disponíveis")
            return None

        if "product_agent" not in cls._components:
            cls.logger.info("Criando nova instância do agente de produtos")
            cls._components["product_agent"] = ProductAgent()

        return cls._components["product_agent"]

    @classmethod
    def reset_component(cls, component_name: str) -> bool:
        """Reinicia um componente específico, removendo sua instância atual

        Args:
            component_name (str): Nome do componente a ser reiniciado

        Returns:
            bool: True se o componente foi reiniciado com sucesso, False caso contrário
        """
        if component_name in cls._components:
            del cls._components[component_name]
            cls.logger.info(f"Componente reiniciado: {component_name}")
            return True

        cls.logger.warning(
            f"Tentativa de reiniciar componente inexistente: {component_name}"
        )
        return False

    @classmethod
    def reset_all(cls) -> None:
        """Reinicia todos os componentes, removendo todas as instâncias atuais"""
        cls._components.clear()
        cls.logger.info("Todos os componentes foram reiniciados")

    @classmethod
    def get_web_server(cls) -> Optional[Any]:
        """Obtém uma instância do servidor web (Flask)"""
        if not FLASK_AVAILABLE:
            cls.logger.error(
                "Flask não está disponível. Instale com 'pip install flask'."
            )
            return None
        if "web_server" not in cls._components:
            from core.config.config_central import ConfiguracaoCentral

            config = ConfiguracaoCentral()
            host = config.web_config.get("host", "127.0.0.1")
            port = config.web_config.get("port", 5000)
            cls.logger.info(f"Criando nova instância do WebServer na porta {port}")
            cls._components["web_server"] = WebServer(host=host, port=port)
        return cls._components["web_server"]


# Exemplo de uso
if __name__ == "__main__":
    # Configura logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Obtém uma instância do adaptador MCP
    mcp = ComponentFactory.get_mcp_adapter()
    if mcp:
        print("Adaptador MCP obtido com sucesso!")

    # Reinicia todos os componentes
    ComponentFactory.reset_all()
    print("Todos os componentes foram reiniciados")
