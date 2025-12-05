"""Runner automático para Streamlit com correções proativas.

Ele inicia o Streamlit usando o Python do venv atual, captura logs e tenta
corrigir erros comuns automaticamente: ModuleNotFoundError (instala o pacote
adequado), UnicodeDecodeError ao ler `.env` (regrava `.env` em UTF-8), e
problemas de install do `numpy` (tenta instalar wheel binário).

Uso: `python tools/autostart_streamlit.py`
"""
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / '.env'
WRITE_ENV_SCRIPT = ROOT / 'tools' / 'write_env.py'

MISSING_MODULE_MAP = {
    'dask': ['dask[array,dataframe]'],
    'pyodbc': ['pyodbc'],
    'openai': ['openai'],
    'langgraph': ['langgraph'],
    'langchain_core': ['langchain-core'],
}

def pip_install(python_exe, pkg):
    print(f'-> Instalando {pkg} ...')
    cmd = [python_exe, '-m', 'pip', 'install', pkg]
    r = subprocess.run(cmd, cwd=ROOT)
    return r.returncode == 0

def try_fix_numpy(python_exe):
    # Tenta instalar numpy via wheel binário (forçar binary)
    print('-> Tentando instalar numpy via wheel binário...')
    cmd = [python_exe, '-m', 'pip', 'install', '--only-binary=:all:', 'numpy==1.26.4']
    r = subprocess.run(cmd, cwd=ROOT)
    return r.returncode == 0

def rewrite_env_utf8():
    if WRITE_ENV_SCRIPT.exists():
        print('-> Regravando .env em UTF-8 usando tools/write_env.py')
        subprocess.run([sys.executable, str(WRITE_ENV_SCRIPT)], cwd=ROOT)
        return True
    # fallback: escrever conteudo simples
    print('-> Regravando .env manualmente (fallback)')
    content = 'GEMINI_API_KEY=""\n'
    ENV_FILE.write_text(content, encoding='utf-8')
    return True

def parse_missing_modules(text):
    # Procura por ModuleNotFoundError: No module named 'xyz'
    modules = set()
    for m in re.findall(r"No module named '(.*?)'", text):
        modules.add(m)
    return list(modules)

def run_streamlit(python_exe):
    max_attempts = 8
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        print(f'=== Tentativa {attempt}/{max_attempts} de iniciar Streamlit ===')
        proc = subprocess.Popen([python_exe, '-m', 'streamlit', 'run', 'streamlit_app.py'], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        collected = ''
        try:
            # Ler linha a linha e imprimir; também armazenar para análise
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                print(line, end='')
                collected += line
                # Detecta UnicodeDecodeError no output
                if 'UnicodeDecodeError' in line:
                    print('==> Detectado UnicodeDecodeError: regravando .env e reiniciando')
                    rewrite_env_utf8()
                    proc.kill()
                    break
                # Detecta erro crítico que encerra app
                if 'ModuleNotFoundError' in line or 'No module named' in line:
                    # continue coletando até o fim para capturar o módulo
                    continue

            proc.wait(timeout=1)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

        # Analisar o texto coletado
        missing = parse_missing_modules(collected)
        if not missing and proc.returncode == 0:
            print('Streamlit iniciou com sucesso.')
            return True

        if missing:
            print('Módulos faltantes detectados:', missing)
            installed_any = False
            for mod in missing:
                pkgs = MISSING_MODULE_MAP.get(mod, [mod])
                for pkg in pkgs:
                    ok = pip_install(python_exe, pkg)
                    installed_any = installed_any or ok
            if installed_any:
                print('Instalação de dependências concluída. Tentando reiniciar...')
                time.sleep(1)
                continue

        # Detectar falha do numpy compilation no output
        if 'Unknown compiler' in collected or 'meson' in collected or 'ERROR: Could not find' in collected:
            print('==> Erro de build detectado (possivelmente numpy). Tentando abordagem binária...')
            if try_fix_numpy(python_exe):
                print('numpy instalado via wheel. Tentando reinstalar requirements...')
                subprocess.run([python_exe, '-m', 'pip', 'install', '-r', 'requirements.txt'], cwd=ROOT)
                continue
            else:
                print('Falha ao instalar numpy via wheel. Interrompendo tentativa automática.')
                return False

        # Se não conseguimos resolver, mostrar trecho final e encerrar
        print('Não foi possível resolver automaticamente os erros. Último log coletado:')
        tail = '\n'.join(collected.splitlines()[-40:])
        print(tail)
        return False

if __name__ == '__main__':
    python_exe = sys.executable
    print('Usando python:', python_exe)
    success = run_streamlit(python_exe)
    if success:
        print('Runner finalizou com sucesso.')
        sys.exit(0)
    else:
        print('Runner terminou com falha.')
        sys.exit(2)
