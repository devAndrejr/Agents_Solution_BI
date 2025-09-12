import logging
import random
import re

from flask import Blueprint, jsonify, request

from core.agents.product_agent import ProductAgent
from core.utils.db_utils import prepare_chart_data

"""
Rotas de consulta geral (preço, produto, top vendidos, estoque)
"""

logger = logging.getLogger(__name__)
query_routes_consulta = Blueprint("query_routes_consulta", __name__)

general_responses = {
    "saudacao": [
        "Olá! Sou o Caçulinha, seu assistente. Como posso ajudar?",
        "Oi! Tudo bem? Sou o Caçulinha, estou aqui para ajudar com informações sobre produtos, vendas e estoque.",
        "Olá! Sou o Caçulinha, seu assistente de BI. O que você gostaria de saber hoje?",
    ],
    "agradecimento": [
        "Por nada! Estou sempre à disposição para ajudar.",
        "Disponha! Se precisar de mais alguma coisa, é só perguntar.",
        "De nada! Fico feliz em poder ajudar. Mais alguma coisa?",
    ],
    "despedida": [
        "Até logo! Foi um prazer ajudar.",
        "Tchau! Volte sempre que precisar.",
        "Até a próxima! Estou sempre por aqui se precisar.",
    ],
    "nao_entendi": [
        "Desculpe, não entendi sua pergunta. Pode reformular?",
        "Hmm, não consegui compreender. Pode explicar de outra forma?",
        "Não entendi completamente. Pode ser mais específico sobre o que você precisa saber?",
    ],
    "limitacao": [
        "Só respondo sobre produtos, preços e estoque 😊",
        "Desculpe, só posso ajudar com informações sobre produtos, vendas e estoque.",
        "Minha especialidade é responder sobre produtos, preços e estoque. Posso ajudar com isso?",
    ],
}


def analyze_query_consulta(query):
    query = query.lower()
    product_code_pattern = re.compile(r"produto\s+(\d+)|código\s+(\d+)|cod\s+(\d+)")
    top_selling_pattern = re.compile(r"(mais vendido|top vendas|produto popular)")
    stock_pattern = re.compile(r"(estoque|inventário)")
    greeting_pattern = re.compile(r"(olá|oi|e aí|bom dia|boa tarde|boa noite|hey)")
    thanks_pattern = re.compile(r"(obrigado|obrigada|valeu|agradeço)")
    goodbye_pattern = re.compile(r"(tchau|adeus|até logo|até mais)")
    help_pattern = re.compile(r"(ajuda|ajudar|o que você faz|como funciona)")
    # Saudações
    if greeting_pattern.search(query):
        return {"response": random.choice(general_responses["saudacao"])}
    if thanks_pattern.search(query):
        return {"response": random.choice(general_responses["agradecimento"])}
    if goodbye_pattern.search(query):
        return {"response": random.choice(general_responses["despedida"])}
    if help_pattern.search(query):
        return {
            "response": "Sou o Caçulinha, seu assistente de BI. Posso ajudar com informações sobre produtos, preços, estoque, vendas e categorias. Por exemplo, você pode me perguntar sobre o preço de um produto específico, os produtos mais vendidos, o estoque por categoria, entre outras coisas."
        }
    # Produto por código
    product_code_match = product_code_pattern.search(query)
    if product_code_match:
        code = next(group for group in product_code_match.groups() if group is not None)
        product_agent = ProductAgent()
        product_result = product_agent.get_product_details(code)
        product = (
            product_result.get("product") if product_result.get("success") else None
        )
        if "preço" in query or "valor" in query or "custa" in query:
            if product:
                price = product.get("preco", "N/A")
                price_str = (
                    f"R$ {float(price):.2f}"
                    if isinstance(price, (int, float))
                    or (isinstance(price, str) and price.replace(".", "").isdigit())
                    else price
                )
                return {
                    "response": f"O preço do produto {code} - {product.get('nome', '')} é {price_str}.",
                    "products": [product],
                }
            else:
                return {
                    "response": f"Não encontrei nenhum produto com o código {code}."
                }
        if product:
            return {
                "response": f"Encontrei informações sobre o produto {code} - {product.get('nome', '')}:",
                "products": [product],
            }
        else:
            return {"response": f"Não encontrei nenhum produto com o código {code}."}
    # Produtos mais vendidos
    if top_selling_pattern.search(query):
        limit = 10
        limit_match = re.search(r"top\s+(\d+)", query)
        if limit_match:
            limit = int(limit_match.group(1))
        chart_data = prepare_chart_data("top_products", limit=limit)
        if chart_data:
            return {
                "response": f"Aqui estão os {limit} produtos mais vendidos:",
                "chart_data": chart_data,
            }
        else:
            return {"response": "Não foi possível obter os produtos mais vendidos."}
    # Estoque
    if stock_pattern.search(query):
        chart_data = prepare_chart_data("stock_by_category")
        if chart_data:
            return {
                "response": "Aqui estão as informações de estoque:",
                "chart_data": chart_data,
            }
        else:
            return {"response": "Não foi possível obter informações de estoque."}
    # Não entendi
    return {"response": random.choice(general_responses["nao_entendi"])}


@query_routes_consulta.route("/consulta", methods=["POST"])
def consulta_geral():
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"success": False, "message": "Consulta não informada"}), 400
        query = data["query"]
        logger.info(f"Processando consulta geral: {query}")
        response_data = analyze_query_consulta(query)
        return jsonify({"success": True, "query": query, **response_data})
    except Exception as e:
        logger.error(f"Erro ao processar consulta geral: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Erro ao processar consulta: {str(e)}"}
            ),
            500,
        )
