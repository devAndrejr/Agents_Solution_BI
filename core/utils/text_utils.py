import locale
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

"""
Utilitários para formatação de texto
"""

# Configura o locale para formatação de números e moedas
try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except:
    try:
        locale.setlocale(locale.LC_ALL, "Portuguese_Brazil.1252")
    except:
        pass  # Usa o locale padrão se não conseguir configurar


def format_currency(value):
    """
    Formata um valor numérico como moeda (R$).

    Args:
        value: Valor numérico a ser formatado

    Returns:
        String formatada como moeda brasileira (R$)
    """
    if value is None:
        return "R$ 0,00"

    try:
        # Tenta converter para float se não for um número
        if not isinstance(value, (int, float)):
            value = float(str(value).replace(",", ".").replace("R$", "").strip())

        # Formata o valor como moeda brasileira
        return locale.currency(value, grouping=True, symbol=True)
    except (ValueError, TypeError):
        # Se não conseguir converter, retorna o valor original como string
        return f"R$ {value}" if value else "R$ 0,00"


def format_number(value, decimal_places=2):
    """
    Formata um número com separadores de milhar e casas decimais.

    Args:
        value: Valor numérico a ser formatado
        decimal_places: Número de casas decimais

    Returns:
        String formatada com separadores de milhar e casas decimais
    """
    if value is None:
        return "0"

    try:
        # Tenta converter para float se não for um número
        if not isinstance(value, (int, float)):
            value = float(str(value).replace(",", ".").strip())

        # Formata o número com separadores de milhar e casas decimais
        return locale.format_string(f"%.{decimal_places}f", value, grouping=True)
    except (ValueError, TypeError):
        # Se não conseguir converter, retorna o valor original como string
        return str(value) if value else "0"


def format_date(date_value, format_str="%d/%m/%Y"):
    """
    Formata uma data para o formato brasileiro.

    Args:
        date_value: Objeto datetime ou string de data
        format_str: Formato de saída da data

    Returns:
        String formatada como data
    """
    if date_value is None:
        return "N/A"

    try:
        # Se for string, tenta converter para datetime
        if isinstance(date_value, str):
            # Tenta diferentes formatos comuns
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"]:
                try:
                    date_value = datetime.strptime(date_value, fmt)
                    break
                except ValueError:
                    continue

        # Formata a data no formato desejado
        if isinstance(date_value, datetime):
            return date_value.strftime(format_str)
        return str(date_value)
    except Exception:
        # Se não conseguir converter, retorna o valor original como string
        return str(date_value) if date_value else "N/A"


if __name__ == "__main__":
    print("Rodando como script...")
    # TODO: Adicionar chamada a uma função principal se necessário
