import argparse
import os
import os.path
import subprocess
import sys

# Adiciona o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.utils.env_setup import setup_environment

setup_environment()

# --- Configuração ---
# Mude para 'ruff' se preferir usar o Ruff Formatter
# FORMATTER = "ruff"
FORMATTER = "black"
# --------------------


def run_formatter(target_path: str):
    """
    Executa a ferramenta de formatação de código no caminho especificado.

    Args:
        target_path (str): O arquivo ou diretório a ser formatado.
    """
    if not os.path.exists(target_path):
        print(f"Erro: O caminho '{target_path}' não foi encontrado.", file=sys.stderr)
        sys.exit(1)

    if FORMATTER == "black":
        command = ["black", target_path]
    elif FORMATTER == "ruff":
        command = ["ruff", "format", target_path]
    else:
        print(f"Erro: Formatador '{FORMATTER}' não reconhecido.", file=sys.stderr)
        sys.exit(1)

    print(f"▶️  Executando '{' '.join(command)}'...")

    try:
        # ==============================================================================
        # ALTERAÇÃO PRINCIPAL AQUI:
        # Trocamos 'encoding="utf-8"' por 'encoding=sys.stdout.encoding' para usar a
        # codificação correta do console do Windows.
        # Adicionamos 'errors="replace"' como um seguro para evitar crashes.
        # ==============================================================================
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding=sys.stdout.encoding,  # <-- MUDANÇA
            errors="replace",  # <-- MUDANÇA
        )

        # Mostra a saída padrão e de erro do formatador
        if result.stdout:
            print("--- Saída do Formatador ---")
            print(result.stdout)
        if result.stderr:
            print("--- Erros do Formatador ---", file=sys.stderr)
            print(result.stderr, file=sys.stderr)

        if result.returncode == 0:
            print(f"✅ Formatação com '{FORMATTER}' concluída com sucesso!")
        else:
            # O código 123 do black geralmente significa um erro interno.
            # Com a correção de encoding, ele não deve mais ocorrer.
            print(
                f"⚠️  Ocorreu um problema durante a formatação. "
                f"Código de saída: {result.returncode}",
                file=sys.stderr,
            )

    except FileNotFoundError:
        print(f"Erro: O comando '{FORMATTER}' não foi encontrado.", file=sys.stderr)
        print(f"Por favor, instale-o com: pip install {FORMATTER}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"Um script para formatar código Python usando {FORMATTER}."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help=(
            "O caminho para o arquivo ou diretório a ser formatado. "
            "Padrão: diretório atual."
        ),
    )
    args = parser.parse_args()

    run_formatter(args.path)
