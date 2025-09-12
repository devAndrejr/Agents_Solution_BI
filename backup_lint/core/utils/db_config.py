import logging

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

try:
    # seu código principal aqui
    pass
except Exception as e:
    logging.error(f"Erro geral: {e}")

"""
Configuração do banco de dados para o agente Caçulinha BI
"""

# Carrega variáveis de ambiente
load_dotenv()

# DB_CONFIG foi movido para core/config/config.py

# Mapeamento de tabelas e colunas importantes
TABLE_MAPPING = {
    "produtos": {
        "table_name": "dbo.Admat_OPCOM",
        "columns": {
            "codigo": "CÓDIGO",
            "nome": "NOME",
            "preco": "PREÇO 38%",
            "fabricante": "FABRICANTE",
            "embalagem": "EMBALAGEM",
            "categoria": "CATEGORIA",
            "grupo": "GRUPO",
            "subgrupo": "SUBGRUPO",
            "estoque": "EST# UNE",
            "ultima_venda": "ULTIMA_VENDA",
        },
    }
}

# Consultas SQL pré-definidas
PREDEFINED_QUERIES = {
    "produto_por_codigo": """
        SELECT
            [CÓDIGO] as codigo,
            [NOME] as nome,
            [PREÇO 38%] as preco,
            [FABRICANTE] as fabricante,
            [EMBALAGEM] as embalagem,
            [CATEGORIA] as categoria,
            [GRUPO] as grupo,
            [SUBGRUPO] as subgrupo,
            [EST# UNE] as estoque,
            [ULTIMA_VENDA] as ultima_venda
        FROM dbo.Admat_OPCOM
        WHERE [CÓDIGO] = {codigo} OR CONVERT(VARCHAR, [CÓDIGO]) = '{codigo_str}'
    """,
    "produto_por_nome": """
        SELECT
            [CÓDIGO] as codigo,
            [NOME] as nome,
            [PREÇO 38%] as preco,
            [FABRICANTE] as fabricante,
            [EMBALAGEM] as embalagem,
            [CATEGORIA] as categoria,
            [GRUPO] as grupo,
            [SUBGRUPO] as subgrupo,
            [EST# UNE] as estoque,
            [ULTIMA_VENDA] as ultima_venda
        FROM dbo.Admat_OPCOM
        WHERE [NOME] LIKE "%{nome}%"
    """,
    "produtos_por_categoria": """
        SELECT
            [CÓDIGO] as codigo,
            [NOME] as nome,
            [PREÇO 38%] as preco,
            [CATEGORIA] as categoria,
            [GRUPO] as grupo,
            [SUBGRUPO] as subgrupo,
            [EST# UNE] as estoque
        FROM dbo.Admat_OPCOM
        WHERE [CATEGORIA] = '{categoria}'
        ORDER BY [NOME]
    """,
    "produtos_mais_vendidos": """
        SELECT TOP 10
            [CÓDIGO] as codigo,
            [NOME] as nome,
            [PREÇO 38%] as preco,
            [VENDA 30D] as vendas_30d,
            [CATEGORIA] as categoria,
            [GRUPO] as grupo
        FROM dbo.Admat_OPCOM
        WHERE [VENDA 30D] > 0
        ORDER BY [VENDA 30D] DESC
    """,
}


# Função para obter a consulta SQL apropriada
def get_query(query_name, **params):
    """
    Retorna a query SQL formatada com os parâmetros fornecidos.
    """
    if query_name not in PREDEFINED_QUERIES:
        raise ValueError(
            f"Query '{query_name}' não está definida em PREDEFINED_QUERIES."
        )
    query = PREDEFINED_QUERIES[query_name]
    # Substitui parâmetros na query
    try:
        return query.format(**params, codigo_str=str(params.get("codigo", "")))
    except KeyError as e:
        raise ValueError(f"Parâmetro ausente para a query: {e}")


if __name__ == "__main__":
    print("Rodando como script...")
    # TODO: Adicionar chamada a uma função principal se necessário
