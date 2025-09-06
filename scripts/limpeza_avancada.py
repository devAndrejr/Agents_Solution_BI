import os
import shutil

RELATORIO_ORIGEM = "relatorio_arquitetura_completo.md"
RELATORIO_DESTINO = "limpeza_arquitetura.md"

# Palavras-chave para exclusão e revisão
KEYWORDS = {
    "excluir": ["__pycache__", ".ipynb_checkpoints", ".tmp", ".bak", "logs", "cache", "lixo", "backup", "remover"],
    "revisar": ["duplicado", "suspeito", "revisar", "avaliar", "possível conflito"],
}

def classificar_linha(linha: str) -> str:
    """Classifica a linha em Excluir ou Revisar com base em palavras-chave."""
    lower_line = linha.lower()
    for categoria, palavras in KEYWORDS.items():
        if any(palavra in lower_line for palavra in palavras):
            return categoria
    return "revisar"

def gerar_relatorio():
    if not os.path.exists(RELATORIO_ORIGEM):
        print(f"❌ Arquivo {RELATORIO_ORIGEM} não encontrado na raiz do projeto.")
        return [], []

    excluir, revisar = [], []

    with open(RELATORIO_ORIGEM, "r", encoding="utf-8") as f:
        for linha in f:
            if not linha.strip():
                continue
            categoria = classificar_linha(linha)
            if categoria == "excluir":
                excluir.append(linha.strip())
            else:
                revisar.append(linha.strip())

    with open(RELATORIO_DESTINO, "w", encoding="utf-8") as f:
        f.write("# Relatório de Limpeza da Arquitetura\n\n")

        f.write("## 🗑️ EXCLUIR (arquivos lixo, temporários, backups)\n")
        f.writelines(f"- {item}\n" for item in excluir) if excluir else f.write("- Nenhum item identificado\n")
        f.write("\n")

        f.write("## ⚠️ REVISAR (duplicações ou pontos suspeitos)\n")
        f.writelines(f"- {item}\n" for item in revisar) if revisar else f.write("- Nenhum item identificado\n")
        f.write("\n")

    print(f"✅ Relatório atualizado em: {RELATORIO_DESTINO}")
    return excluir, revisar

def excluir_arquivos(lista_excluir):
    """Exclui arquivos e pastas listados com confirmação do usuário."""
    if not lista_excluir:
        print("⚠️ Nenhum arquivo para excluir.")
        return

    print("\n🔎 Arquivos/Pastas identificados para exclusão:")
    for item in lista_excluir:
        print(f" - {item}")

    confirm = input("\n❓ Deseja realmente excluir esses itens? (s/N): ").strip().lower()
    if confirm != "s":
        print("❌ Exclusão cancelada.")
        return

    for item in lista_excluir:
        caminho = item.replace("-", "").strip()  # limpa formatação do relatório
        if os.path.exists(caminho):
            try:
                if os.path.isfile(caminho):
                    os.remove(caminho)
                elif os.path.isdir(caminho):
                    shutil.rmtree(caminho)
                print(f"🗑️ Excluído: {caminho}")
            except Exception as e:
                print(f"❌ Erro ao excluir {caminho}: {e}")
        else:
            print(f"⚠️ Caminho não encontrado: {caminho}")

    print("\n✅ Exclusão concluída!")

if __name__ == "__main__":
    excluir, revisar = gerar_relatorio()
    excluir_arquivos(excluir)
