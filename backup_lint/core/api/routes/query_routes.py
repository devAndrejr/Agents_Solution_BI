from flask import Blueprint

from core.api.routes.query_routes_analise import query_routes_analise
from core.api.routes.query_routes_consulta import query_routes_consulta
from core.api.routes.query_routes_historico import query_routes_historico

# Blueprint principal para registrar todos os sub-blueprints
query_routes = Blueprint("query_routes", __name__)

# Registro dos blueprints de sub-rotas
query_routes.register_blueprint(query_routes_consulta)
query_routes.register_blueprint(query_routes_historico)
query_routes.register_blueprint(query_routes_analise)

# As funções e rotas de consulta geral, histórico e análise foram movidas para módulos próprios.


@query_routes.route("/", methods=["GET", "POST"])
def query_root():
    return {"success": True, "message": "Endpoint /api/query está ativo."}, 200
