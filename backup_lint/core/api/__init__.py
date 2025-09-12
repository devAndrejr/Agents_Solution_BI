import logging
import os

from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração de caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_DIR = os.path.join(BASE_DIR, "web", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "web", "static")

# Variável global para o limiter
limiter = None


# Função para registrar todas as rotas da API no aplicativo Flask
def register_routes(app, rate_limiter=None):
    """
    Registra todas as rotas da API no aplicativo Flask

    Args:
        app: Instância do aplicativo Flask
        rate_limiter: Instância do Flask-Limiter (opcional)
    """
    global limiter
    limiter = rate_limiter

    try:
        # Importa os blueprints das rotas
        from .routes.chat_routes import chat_routes
        from .routes.frontend_routes import \
            frontend  # Importa blueprint visual
        from .routes.product_routes import product_routes
        from .routes.query_routes import query_routes

        # Registra os blueprints no aplicativo
        app.register_blueprint(chat_routes)
        app.register_blueprint(product_routes, url_prefix="/api/products")
        app.register_blueprint(query_routes, url_prefix="/api/query")
        app.register_blueprint(frontend)  # Registra rotas visuais

        # Adiciona rota de status da API
        @app.route("/api/status", methods=["GET"])
        def api_status():
            return jsonify(
                {
                    "status": "online",
                    "message": "Sistema funcionando normalmente",
                    "version": "1.0.0",
                }
            )

        logger.info("Rotas da API registradas com sucesso")

        # Lista todas as rotas registradas para depuração
        routes = []
        for rule in app.url_map.iter_rules():
            route_methods = ",".join(rule.methods)
            routes.append(f"{rule.endpoint}: {route_methods} {rule.rule}")

        logger.debug(f"Rotas disponíveis: {routes}")

    except Exception as e:
        logger.error(f"Erro ao registrar rotas da API: {e}")
        raise


def create_app():
    """
    Factory para criar a aplicação Flask e registrar as rotas.
    """
    app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

    # Configuração da chave secreta para sessões Flask
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "caculinha-dev-secret-key")

    # Configuração do rate limiting
    rate_limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
    )

    from . import register_routes

    register_routes(app, rate_limiter)

    @app.route("/", methods=["GET"])
    def welcome():
        return jsonify(
            {
                "message": "Bem-vindo à API Caçulinha BI!",
                "status": "online",
                "docs": "/api/status",
            }
        )

    return app


if __name__ == "__main__":
    print("Módulo de API - Este arquivo não deve ser executado diretamente.")
