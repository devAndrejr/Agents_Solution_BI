import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta

LOG_DIR = os.path.join(os.getcwd(), "logs")
REPORT_MD = os.path.join(
    LOG_DIR, f'relatorio_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
)
REPORT_JSON = os.path.join(
    LOG_DIR, f'relatorio_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
)

LOG_LEVELS = ["ERROR", "WARNING", "INFO", "DEBUG"]

HELP = """
Script de Análise Automática de Logs

Uso:
  python scripts/analisar_logs.py [--help]

Gera relatórios automáticos dos arquivos de log em logs/.
--data-inicial YYYY-MM-DD (opcional)
--data-final YYYY-MM-DD (opcional)
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Análise automática de logs com filtro de datas."
    )
    parser.add_argument(
        "--data-inicial",
        type=str,
        default=None,
        help="Data inicial (YYYY-MM-DD) para filtrar eventos",
    )
    parser.add_argument(
        "--data-final",
        type=str,
        default=None,
        help="Data final (YYYY-MM-DD) para filtrar eventos",
    )
    return parser.parse_args()


def analisar_logs(data_inicial=None, data_final=None):
    log_files = [f for f in os.listdir(LOG_DIR) if f.endswith(".log")]
    resumo = {}
    erros_frequentes = Counter()
    arquivos_criticos = defaultdict(int)
    linhas_criticas = defaultdict(list)
    contagem_niveis = Counter()

    # Preparar datas para filtro
    dt_ini = datetime.strptime(data_inicial, "%Y-%m-%d") if data_inicial else None
    dt_fim = (
        datetime.strptime(data_final, "%Y-%m-%d") + timedelta(days=1)
        if data_final
        else None
    )

    for log_file in log_files:
        path = os.path.join(LOG_DIR, log_file)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                # Tentar extrair data da linha (formato mais comum: 2025-05-22 21:13:03,798)
                data_evento = None
                for level in LOG_LEVELS:
                    if level in line:
                        # Extrair data se possível
                        try:
                            partes = line.split()
                            for p in partes:
                                if len(p) >= 10 and p[4] == "-" and p[7] == "-":
                                    data_evento = datetime.strptime(
                                        p[:19], "%Y-%m-%d %H:%M:%S"
                                    )
                                    break
                        except Exception:
                            pass
                        # Filtrar por data
                        if (dt_ini and (not data_evento or data_evento < dt_ini)) or (
                            dt_fim and (not data_evento or data_evento >= dt_fim)
                        ):
                            break  # pula linha fora do intervalo
                        contagem_niveis[level] += 1
                        if level in ["ERROR", "WARNING"]:
                            msg = line.strip()
                            erros_frequentes[msg] += 1
                            arquivos_criticos[log_file] += 1
                            linhas_criticas[log_file].append((i, msg))
                        break
    # Pontos de atenção automáticos
    sugestoes = []
    if contagem_niveis["ERROR"] > 0:
        sugestoes.append(
            "Há erros registrados nos logs. Priorize a análise dos arquivos com mais ocorrências."
        )
    if contagem_niveis["WARNING"] > 0:
        sugestoes.append("Existem warnings que podem indicar problemas futuros.")
    if not sugestoes:
        sugestoes.append(
            "Nenhum erro ou warning encontrado. Sistema aparentemente estável."
        )

    resumo = {
        "contagem_niveis": dict(contagem_niveis),
        "erros_mais_frequentes": erros_frequentes.most_common(10),
        "arquivos_mais_criticos": sorted(
            arquivos_criticos.items(), key=lambda x: -x[1]
        )[:5],
        "linhas_criticas": {k: v[:5] for k, v in linhas_criticas.items()},
        "sugestoes": sugestoes,
    }

    # Gerar relatório Markdown
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(
            f"# Relatório Automático de Logs - "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        )
        f.write("## Contagem por Nível\n")
        for level, count in contagem_niveis.items():
            f.write(f"- **{level}**: {count}\n")
        f.write("\n## Erros/Warnings Mais Frequentes\n")
        for msg, count in erros_frequentes.most_common(10):
            f.write(f"- ({count}x) {msg[:200]}\n")
        f.write("\n## Arquivos Mais Críticos\n")
        for fname, count in sorted(arquivos_criticos.items(), key=lambda x: -x[1])[:5]:
            f.write(f"- {fname}: {count} ocorrências\n")
        f.write("\n## Exemplos de Linhas Críticas\n")
        for fname, linhas in linhas_criticas.items():
            f.write(f"### {fname}\n")
            for i, msg in linhas[:5]:
                f.write(f"- Linha {i}: {msg[:200]}\n")
        f.write("\n## Sugestões Automáticas\n")
        for s in sugestoes:
            f.write(f"- {s}\n")
    # Gerar relatório JSON
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)
    print(f"Relatórios gerados:\n- {REPORT_MD}\n- {REPORT_JSON}")


if __name__ == "__main__":
    args = parse_args()
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(HELP)
    else:
        analisar_logs(data_inicial=args.data_inicial, data_final=args.data_final)
