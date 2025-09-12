import os
import sys

from flasgger import Swagger
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit, join_room
from flask_talisman import Talisman

# Adiciona o diretório raiz ao path antes das importações
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from core.api import create_app
from core.config.config import Config
from core.utils.env_setup import setup_environment

# Inicializa SocketIO sem app (será associado depois)
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")

if __name__ == "__main__":
    setup_environment()
    app = create_app()

    # Configuração do rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
    )

    # Configuração do Swagger (Flasgger)
    swagger = Swagger(
        app,
        template={
            "swagger": "2.0",
            "info": {
                "title": "Agent BI API",
                "description": "Documentação interativa dos endpoints do Agent BI.",
                "version": "1.0.0",
            },
            "basePath": "/",
            "schemes": ["http", "https"],
        },
    )

    # Configuração básica do Flask-Talisman para headers de segurança
    Talisman(
        app,
        content_security_policy={
            "default-src": [
                "'self'",
                "https://cdn.jsdelivr.net",
                "https://cdnjs.cloudflare.com",
                "https://fonts.googleapis.com",
                "https://fonts.gstatic.com",
            ],
            "img-src": ["'self'", "data:", "https://raw.githubusercontent.com"],
            "script-src": [
                "'self'",
                "https://cdn.jsdelivr.net",
                "https://cdnjs.cloudflare.com",
            ],
            "style-src": [
                "'self'",
                "https://cdn.jsdelivr.net",
                "https://cdnjs.cloudflare.com",
                "https://fonts.googleapis.com",
            ],
            "font-src": [
                "'self'",
                "https://fonts.gstatic.com",
                "https://cdnjs.cloudflare.com",
            ],
        },
        force_https=False,  # Mudado para False para desenvolvimento local
        strict_transport_security=True,
        frame_options="DENY",
        referrer_policy="no-referrer",
        session_cookie_secure=False,  # Mudado para False para desenvolvimento local
        session_cookie_http_only=True,
        session_cookie_samesite="Lax",
    )

    # Associa o app ao SocketIO
    socketio.init_app(app)

    # Exemplo: autenticação simples para admin (ajuste conforme seu sistema)
    @socketio.on("connect")
    def handle_connect():
        user = getattr(request, "user", None)
        if user and getattr(user, "is_admin", False):
            join_room("admins")
            emit(
                "admin_notification",
                {"type": "info", "message": "Bem-vindo ao painel admin!"},
                room=request.sid,
            )
        # else: pode desconectar não-admins se quiser

    # Endpoint para emitir notificação de exemplo (pode ser chamado por evento real)
    @app.route("/api/admin/notify", methods=["POST"])
    @limiter.limit("10 per minute")
    def notify_admin():
        data = request.json
        socketio.emit(
            "admin_notification",
            {
                "type": data.get("type", "info"),
                "message": data.get("message", "Notificação para admins"),
            },
            room="admins",
        )
        return {"success": True}

    print("DB_SERVER:", os.getenv("DB_SERVER"))
    print("DB_DATABASE:", os.getenv("DB_DATABASE"))
    print("DB_USER:", os.getenv("DB_USER"))
    print("DB_PASSWORD:", os.getenv("DB_PASSWORD"))
    print("DB_DRIVER:", os.getenv("DB_DRIVER"))
    print("SQLALCHEMY_DATABASE_URI:", Config().SQLALCHEMY_DATABASE_URI)

    # Rodar Flask em modo single-thread/processo
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, threaded=False)
