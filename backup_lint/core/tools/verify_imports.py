import importlib

"""
Script para verificar se as importações funcionam corretamente.
"""


def check_import(module_name):
    try:
        importlib.import_module(module_name)
        print(f"✓ Importação de '{module_name}' bem-sucedida")
        return True
    except ImportError as e:
        print(f"✗ Erro ao importar '{module_name}': {e}")
        return False


# Lista de módulos para verificar
modules_to_check = [
    "langchain_core.messages",
    "langchain_openai",
    "langgraph.graph",
    "langchain_community.utilities",
    "sqlalchemy",
    "dotenv",
]

print("Verificando importações críticas...")
all_passed = True

for module in modules_to_check:
    if not check_import(module):
        all_passed = False

if all_passed:
    print("\nTodas as importações funcionam corretamente!")
    print("Se você ainda vê erros no VS Code, tente:")
    print("1. Reiniciar o VS Code")
    print(
        "2. Selecionar o interpretador Python correto (Ctrl+Shift+P -> Python: Select Interpreter)"
    )
    print("3. Verificar se o arquivo .vscode/settings.json foi criado corretamente")
else:
    print("\nAlgumas importações falharam. Verifique os erros acima.")
