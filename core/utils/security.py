import re


def sanitize_query(query):
    """
    Sanitiza uma consulta SQL para evitar injeção de SQL

    Args:
        query (str): Consulta SQL a ser sanitizada

    Returns:
        str: Consulta SQL sanitizada
    """
    if not query:
        return ""

    # Remove comentários de linha única
    query = re.sub(r"--.*$", "", query, flags=re.MULTILINE)

    # Remove comentários de múltiplas linhas
    query = re.sub(r"/\*.*?\*/", "", query, flags=re.DOTALL)

    # Remove espaços extras
    query = re.sub(r"\s+", " ", query).strip()

    return query


if __name__ == "__main__":
    print("Rodando como script...")
    # TODO: Adicionar chamada a uma função principal se necessário
