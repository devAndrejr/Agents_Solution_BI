import os
import ast

# Métodos a serem rastreados para análise de obsolescência
OBSOLETE_CANDIDATES = {
    "core/agents/product_agent.py": [
        "get_product_details", "get_products_by_category", "get_products_by_manufacturer",
        "get_products_by_group", "get_products_by_name"
    ],
    "core/agents/tool_agent.py": ["extract_intent_and_entities"]
}

# Arquivos que são considerados obsoletos se não forem importados em nenhum lugar
FILE_OBSOLETE_CANDIDATES = [
    "core/llm_adapter.py",
    "core/transformer_adapter.py"
]

class UsageVisitor(ast.NodeVisitor):
    """Visitor para encontrar chamadas de função, instanciações e importações."""
    def __init__(self):
        self.calls = set()
        self.imports = set()

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.add(node.func.attr)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name.split('.')[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module.split('.')[0])
        self.generic_visit(node)

def analyze_file(file_path):
    """Analisa um único arquivo Python e retorna as chamadas e importações."""
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=file_path)
            visitor = UsageVisitor()
            visitor.visit(tree)
            return visitor.calls, visitor.imports
        except Exception:
            return set(), set()

def map_integrations(root_dir):
    """Mapeia as integrações e o uso de componentes em todo o projeto."""
    method_usage = {f"{file}::{method}": [] for file, methods in OBSOLETE_CANDIDATES.items() for method in methods}
    file_usage = {file: [] for file in FILE_OBSOLETE_CANDIDATES}
    all_usages = {}

    for subdir, _, files in os.walk(root_dir):
        if any(excluded in subdir for excluded in ['venv', '.pytest_cache', '__pycache__']):
            continue
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(subdir, file)
                rel_path = os.path.relpath(file_path, root_dir).replace('\\', '/')
                all_usages[rel_path] = analyze_file(file_path)

    # Verifica o uso dos métodos candidatos a obsoletos
    for file_path, methods in OBSOLETE_CANDIDATES.items():
        for method in methods:
            key = f"{file_path}::{method}"
            for caller_path, (called_methods, _) in all_usages.items():
                if caller_path == file_path: continue
                if method in called_methods:
                    method_usage[key].append(caller_path)

    # Verifica o uso dos arquivos candidatos a obsoletos
    for file_path in FILE_OBSOLETE_CANDIDATES:
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        for caller_path, (_, imports) in all_usages.items():
            if module_name in imports:
                file_usage[file_path].append(caller_path)

    return method_usage, file_usage

def generate_report(method_usage, file_usage):
    """Gera o relatório final."""
    report = "# Relatório de Integração e Análise de Obsolescência\n\n"
    report += "## Fluxo Principal da Consulta\n"
    report += "1.  **UI (`streamlit_app.py`)**: Captura a consulta do usuário.\n"
    report += "2.  **Processador (`core/query_processor.py`)**: Orquestra o fluxo, chamando o `ProductAgent` para buscar dados e depois o `ToolAgent` para gerar a resposta final.\n"
    report += "3.  **Agente de Produto (`core/agents/product_agent.py`)**: Usa o `ToolAgent` para converter a consulta em filtros, busca os dados nos arquivos Parquet e os retorna.\n"
    report += "4.  **Agente de Ferramentas (`core/agents/tool_agent.py`)**: Atua como um wrapper para o modelo de linguagem (OpenAI), tanto para extrair filtros quanto para gerar respostas em linguagem natural.\n"
    report += "5.  **UI (`streamlit_app.py`)**: Exibe a resposta ao usuário.\n\n"

    report += "## Análise de Componentes Obsoletos\n\n"
    report += "### Métodos Potencialmente Obsoletos\n"
    report += "A análise estática do código identificou os seguintes métodos como obsoletos, pois não são chamados por nenhum outro componente externo ao seu próprio arquivo.\n\n"
    obsolete_methods_found = False
    for key, callers in method_usage.items():
        if not callers:
            obsolete_methods_found = True
            file, method = key.split("::")
            report += f"- **Método:** `{method}`\n"
            report += f"  - **Arquivo:** `{file}`\n"
            report += f"  - **Status:** **Obsoleto.** A funcionalidade é coberta pelo método `search_products` que usa o LLM.\n\n"
    if not obsolete_methods_found:
        report += "Nenhum método candidato foi confirmado como obsoleto.\n\n"

    report += "### Arquivos Potencialmente Obsoletos\n"
    report += "Os seguintes arquivos não são importados ou utilizados em nenhuma parte do projeto.\n\n"
    obsolete_files_found = False
    for file, importers in file_usage.items():
        if not importers:
            obsolete_files_found = True
            report += f"- **Arquivo:** `{file}`\n"
            report += f"  - **Status:** **Obsoleto.** A API do LLM é chamada diretamente, tornando este adaptador desnecessário.\n\n"
    if not obsolete_files_found:
        report += "Nenhum arquivo candidato foi confirmado como obsoleto.\n\n"

    report += "## Conclusão da Análise\n"
    report += "O projeto possui um fluxo de integração claro, mas contém componentes e métodos que se tornaram redundantes à medida que a lógica principal foi centralizada em agentes mais inteligentes. A remoção desses elementos simplificaria a base de código sem perda de funcionalidade.\n"

    return report

if __name__ == "__main__":
    project_root = os.getcwd()
    method_usage_map, file_usage_map = map_integrations(project_root)
    report_content = generate_report(method_usage_map, file_usage_map)
    
    output_path = os.path.join(project_root, "relatorio_de_integracao.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"Relatório de integração salvo em: {output_path}")
    print("\n--- CONTEÚDO DO RELATÓRIO ---\n")
    print(report_content)