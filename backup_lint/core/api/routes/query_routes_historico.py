import logging
import re

from flask import Blueprint, jsonify, request

from core.agents.product_agent import ProductAgent
from core.utils.db_utils import prepare_chart_data

"""
Rotas de histórico de vendas e consultas temporais
"""

logger = logging.getLogger(__name__)
query_routes_historico = Blueprint("query_routes_historico", __name__)


@query_routes_historico.route("/historico", methods=["POST"])
def historico_vendas():
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"success": False, "message": "Consulta não informada"}), 400
        query = data["query"].lower()
        # Histórico de vendas por produto
        sales_history_pattern = re.compile(
            r"histórico\s+(?:de\s+)?vendas\s+(?:do\s+)?(?:produto\s+)?(\d+)"
        )
        match = sales_history_pattern.search(query)
        if match:
            code = match.group(1)
            chart_data = prepare_chart_data("sales_history", product_code=code)
            if chart_data:
                return jsonify(
                    {
                        "success": True,
                        "response": f"Aqui está o histórico de vendas do produto {code}:",
                        "chart_data": chart_data,
                    }
                )
            else:
                return jsonify(
                    {
                        "success": False,
                        "response": f"Não foi possível obter histórico de vendas do produto {code}.",
                    }
                )
        return jsonify(
            {
                "success": False,
                "response": "Não foi possível identificar a consulta de histórico de vendas.",
            }
        )
    except Exception as e:
        logger.error(f"Erro ao processar histórico de vendas: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Erro ao processar histórico: {str(e)}"}
            ),
            500,
        )
