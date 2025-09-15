import os

RELATORIO_ORIGEM = "relatorio_arquitetura_completo.md"
RELATORIO_DESTINO = "limpeza_arquitetura.md"

# Palavras-chave para classificação
KEYWORDS = {
    "mover": ["mover", "realocar", "reposicionar"],
    "excluir": ["excluir", "apagar", "remover", "desnecessário", "lixo", "backup", "tmp", "cache"],
    "revisar": ["duplicado", "suspeito", "revisar", "verificar", "avaliar", "possível conflito"],
}

def classificar_linha(linha: str) -> str:
    """Classifica a linha em Mover, Excluir ou Revisar com base em palavras-chave."""
    lower_line = linha.lower()
    for categoria, palavras in KEYWORDS.items():
        if any(palavra in lower_line for palavra in palavras):
            return categoria
    return "revisar"  # padrão seguro

def gerar_relatorio():
    if not os.path.exists(RELATORIO_ORIGEM):
        print(f"❌ Arquivo {RELATORIO_ORIGEM} não encontrado na raiz do projeto.")
        return

    mover, excluir, revisar = [], [], []

    with open(RELATORIO_ORIGEM, "r", encoding="utf-8") as f:
        for linha in f:
            if not linha.strip():
                continue
            categoria = classificar_linha(linha)
            if categoria == "mover":
                mover.append(linha.strip())
            elif categoria == "excluir":
                excluir.append(linha.strip())
            else:
                revisar.append(linha.strip())

    with open(RELATORIO_DESTINO, "w", encoding="utf-8") as f:
        f.write("# Relatório de Limpeza da Arquitetura\n\n")
        
        f.write("## 📂 MOVER (arquivos mal posicionados)\n")
        f.writelines(f"- {item}\n" for item in mover) if mover else f.write("- Nenhum item identificado\n")
        f.write("\n")

        f.write("## 🗑️ EXCLUIR (arquivos lixo, temporários, backups)\n")
        f.writelines(f"- {item}\n" for item in excluir) if excluir else f.write("- Nenhum item identificado\n")
        f.write("\n")

        f.write("## ⚠️ REVISAR (duplicações ou pontos suspeitos)\n")
        f.writelines(f"- {item}\n" for item in revisar) if revisar else f.write("- Nenhum item identificado\n")
        f.write("\n")

    print(f"✅ Relatório gerado com sucesso em: {RELATORIO_DESTINO}")


if __name__ == "__main__":
    gerar_relatorio()
