import os
import ast
from pathlib import Path
from collections import defaultdict


def listar_arquivos(base_path="."):
    """Lista todos os arquivos e subpastas recursivamente"""
    inventario = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            caminho = os.path.join(root, file)
            inventario.append(caminho)
    return inventario


def analisar_imports(filepath):
    """Analisa imports em arquivos .py para mapear dependências internas"""
    dependencias = []
    if filepath.endswith(".py"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=filepath)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dependencias.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            dependencias.append(node.module)
        except Exception as e:
            dependencias.append(f"Erro parsing: {e}")
    return dependencias


def normalizar_modulo(filepath, base_path="."):
    """Converte caminho de arquivo em nome de módulo Python"""
    if not filepath.endswith(".py"):
        return None
    rel_path = os.path.relpath(filepath, base_path)
    sem_ext = rel_path.replace(".py", "")
    return sem_ext.replace(os.sep, ".")


def gerar_relatorio(base_path="."):
    """Gera relatório completo da estrutura e dependências"""
    inventario = listar_arquivos(base_path)
    relatorio = []
    grafo_dependencias = defaultdict(list)
    modulos = {}

    for arquivo in inventario:
        deps = analisar_imports(arquivo)
        modulo = normalizar_modulo(arquivo, base_path)
        if modulo:
            modulos[modulo] = arquivo
            for d in deps:
                grafo_dependencias[modulo].append(d)
        relatorio.append({
            "arquivo": arquivo,
            "modulo": modulo,
            "dependencias": deps
        })

    # Detectar arquivos órfãos (não importados por ninguém)
    usados = set()
    for deps in grafo_dependencias.values():
        usados.update(deps)

    modulos_usados = {m for m in modulos if any(
        m.startswith(u) for u in usados)}
    modulos_orfaos = set(modulos.keys()) - modulos_usados

    # Detectar duplicações de pastas (ex: core/core)
    duplicacoes = []
    for root, dirs, files in os.walk(base_path):
        nomes = [d.lower() for d in dirs]
        repetidos = {n for n in nomes if nomes.count(n) > 1}
        if repetidos:
            duplicacoes.append((root, repetidos))

    return relatorio, grafo_dependencias, modulos_orfaos, duplicacoes


if __name__ == "__main__":
    base = Path(".")
    relatorio, grafo, orfaos, duplicacoes = gerar_relatorio(base)

    with open("relatorio_arquitetura_completo.md", "w", encoding="utf-8") as f:
        f.write("# 📊 Relatório Completo de Arquitetura e Dependências\n\n")

        f.write("## 📂 Estrutura e Dependências por Arquivo\n\n")
        for item in relatorio:
            f.write(f"### {item['arquivo']}\n")
            if item["modulo"]:
                f.write(f"- Módulo: `{item['modulo']}`\n")
            if item['dependencias']:
                f.write("**Imports/Dependências:**\n")
                for d in item['dependencias']:
                    f.write(f"- {d}\n")
            else:
                f.write("_Sem dependências detectadas_\n")
            f.write("\n---\n\n")

        f.write("## 🔗 Grafo de Dependências\n\n")
        for modulo, deps in grafo.items():
            f.write(f"- `{modulo}` importa:\n")
            for d in deps:
                f.write(f"  - {d}\n")
            f.write("\n")

        f.write("## ❌ Arquivos/Módulos Órfãos (não importados por ninguém)\n\n")
        if orfaos:
            for m in orfaos:
                f.write(f"- {m}\n")
        else:
            f.write("_Nenhum módulo órfão detectado_\n")
        f.write("\n---\n\n")

        f.write("## ⚠️ Duplicações de Pastas\n\n")
        if duplicacoes:
            for root, reps in duplicacoes:
                f.write(
                    f"- Na pasta `{root}` existem duplicações: {', '.join(reps)}\n")
        else:
            f.write("_Nenhuma duplicação detectada_\n")
        f.write("\n---\n\n")

        f.write("## 🗑️ Sugestões de Limpeza\n\n")
        f.write("- Verifique os módulos órfãos: podem ser removidos ou movidos.\n")
        f.write("- Revise duplicações de pastas (ex: `core/core`) e unifique.\n")
        f.write(
            "- Confirme se `supervisor_agents.py` deve estar na raiz ou em `core/agents`.\n")
        f.write("- Avalie se cada módulo tem responsabilidade única (SRP).\n")
        f.write(
            "- Separe código de infraestrutura (db, configs) de código de negócio (agentes).\n")

    print("✅ Relatório gerado em relatorio_arquitetura_completo.md")
