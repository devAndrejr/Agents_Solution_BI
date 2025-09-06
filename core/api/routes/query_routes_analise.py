import logging
import re

from flask import Blueprint, jsonify, request

from core.agents.product_agent import ProductAgent
from core.utils.db_utils import prepare_chart_data

"""
Rotas de análise, gráficos e agregações
"""

logger = logging.getLogger(__name__)
query_routes_analise = Blueprint("query_routes_analise", __name__)


@query_routes_analise.route("/analise", methods=["POST"])
def analise_categoria():
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"success": False, "message": "Consulta não informada"}), 400
        query = data["query"].lower()
        # Vendas por categoria
        category_sales_pattern = re.compile(r"(vendas por categoria|categoria)")
        if category_sales_pattern.search(query):
            chart_data = prepare_chart_data("category_sales")
            if chart_data:
                return jsonify(
                    {
                        "success": True,
                        "response": "Aqui estão as vendas por categoria:",
                        "chart_data": chart_data,
                    }
                )
            else:
                return jsonify(
                    {
                        "success": False,
                        "response": "Não foi possível obter informações sobre vendas por categoria.",
                    }
                )
        # Estoque por categoria
        stock_pattern = re.compile(r"(estoque|inventário)")
        if stock_pattern.search(query) and "categoria" in query:
            chart_data = prepare_chart_data("stock_by_category")
            if chart_data:
                return jsonify(
                    {
                        "success": True,
                        "response": "Aqui está a distribuição de estoque por categoria:",
                        "chart_data": chart_data,
                    }
                )
            else:
                return jsonify(
                    {
                        "success": False,
                        "response": "Não foi possível obter informações sobre estoque por categoria.",
                    }
                )
        return jsonify(
            {
                "success": False,
                "response": "Não foi possível identificar a consulta de análise.",
            }
        )
    except Exception as e:
        logger.error(f"Erro ao processar análise: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Erro ao processar análise: {str(e)}"}
            ),
            500,
        )
