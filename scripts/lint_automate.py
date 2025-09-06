import importlib.util
import os
import shutil
import subprocess
from datetime import datetime

# Diretórios a ignorar
IGNORE_DIRS = {"venv", ".git", "__pycache__", "backup_lint"}
BACKUP_DIR = "backup_lint"
RELATORIO = "relatorio_lint_automacao.txt"

# Comandos das ferramentas
AUTOFLAKE_CMD = [
    "python",
    "-m",
    "autoflake",
    "--remove-all-unused-imports",
    "--remove-unused-variables",
    "--in-place",
    "--expand-star-imports",
    "--recursive",
]
BLACK_CMD = ["black"]
ISORT_CMD = ["isort", "--profile", "black"]


def listar_pyfiles(root_dir):
    pyfiles = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove dirs ignorados
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fname in filenames:
            if fname.endswith(".py"):
                fullpath = os.path.join(dirpath, fname)
                pyfiles.append(fullpath)
    return pyfiles


def backup_arquivo(src, root_dir):
    relpath = os.path.relpath(src, root_dir)
    dst = os.path.join(BACKUP_DIR, relpath)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def rodar_cmd(cmd, files):
    """Executa um comando de subprocesso com a lista de arquivos."""
    try:
        subprocess.run(cmd + files, check=True, capture_output=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode()


def main():
    root_dir = os.path.abspath(os.path.dirname(__file__)).replace("scripts", "")
    pyfiles = listar_pyfiles(root_dir)
    alterados = []
    os.makedirs(BACKUP_DIR, exist_ok=True)
    relatorio = []
    relatorio.append(f"Relatório de automação de lint - {datetime.now()}\n")
    relatorio.append(f"Arquivos processados: {len(pyfiles)}\n")
    for f in pyfiles:
        backup = backup_arquivo(f, root_dir)
        relatorio.append(f"Backup: {f} -> {backup}")
    # Checar se autoflake está instalado
    autoflake_spec = importlib.util.find_spec("autoflake")
    if autoflake_spec is not None:
        ok, err = rodar_cmd(AUTOFLAKE_CMD, pyfiles)
        relatorio.append(f"autoflake: {'OK' if ok else 'ERRO'}")
        if err:
            relatorio.append(f"autoflake erro: {err}")
    else:
        relatorio.append(
            "autoflake: NÃO INSTALADO - Instale com 'pip install autoflake' para remover imports/variáveis não usados."
        )
    # Rodar black
    ok, err = rodar_cmd(BLACK_CMD, pyfiles)
    relatorio.append(f"black: {'OK' if ok else 'ERRO'}")
    if err:
        relatorio.append(f"black erro: {err}")
    # Rodar isort
    ok, err = rodar_cmd(ISORT_CMD, pyfiles)
    relatorio.append(f"isort: {'OK' if ok else 'ERRO'}")
    if err:
        relatorio.append(f"isort erro: {err}")
    # Listar arquivos alterados
    for f in pyfiles:
        backup = os.path.join(BACKUP_DIR, os.path.relpath(f, root_dir))
        if os.path.exists(backup):
            with open(f, "r", encoding="utf-8") as f1, open(
                backup, "r", encoding="utf-8"
            ) as f2:
                conteudo_atual = f1.read()
                conteudo_backup = f2.read()
            if conteudo_atual != conteudo_backup:
                alterados.append(f)
    relatorio.append(f"\nArquivos alterados ({len(alterados)}):")
    for f in alterados:
        relatorio.append(f"- {f}")
    # Salvar relatório
    with open(RELATORIO, "w", encoding="utf-8") as f:
        f.write("\n".join(relatorio))
    print(f"Processo concluído! Relatório salvo em {RELATORIO}.")


if __name__ == "__main__":
    main()
