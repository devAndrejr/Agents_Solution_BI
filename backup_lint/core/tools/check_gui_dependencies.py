import subprocess
import sys

"""
Verifica se todas as dependências necessárias para a interface gráfica estão instaladas.
"""


def check_dependency(module_name):
    """Verifica se um módulo está instalado e tenta instalá-lo se não estiver."""
    try:
        print(f"✓ {module_name} já está instalado")
        return True
    except ImportError:
        print(f"✗ {module_name} não está instalado. Tentando instalar...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
            print(f"✓ {module_name} foi instalado com sucesso")
            return True
        except subprocess.CalledProcessError:
            print(f"✗ Falha ao instalar {module_name}")
            return False


def main():
    """Função principal para verificar dependências."""
    print("Verificando dependências para a interface gráfica...")

    # Lista de dependências necessárias
    dependencies = [
        "streamlit",
        "langchain",
        "langchain_openai",
        "langchain_community",
        "sqlalchemy",
        "pyodbc",
        "python-dotenv",
    ]

    all_installed = True
    for dep in dependencies:
        if not check_dependency(dep):
            all_installed = False

    if all_installed:
        print("\nTodas as dependências estão instaladas!")
        print(
            "Você pode executar a interface Streamlit com: streamlit run streamlit_app.py"
        )
    else:
        print("\nAlgumas dependências não puderam ser instaladas.")
        print("Por favor, instale-as manualmente e tente novamente.")


if __name__ == "__main__":
    main()
