import os
import json
from pathlib import Path
from typing import List, Dict

# ============================================================
# INDEXACAO SIMPLIFICADA E ROBUSTA DO CODIGO-FONTE
# ============================================================

CODE_DIR = "./"
PERSIST_DIR = "./storage"
INDEX_FILE = os.path.join(PERSIST_DIR, "code_index.json")

def get_python_files(directory: str, exclude_dirs: List[str] = None) -> List[str]:
    """Encontra todos os arquivos Python no diretório."""
    if exclude_dirs is None:
        exclude_dirs = ['venv', 'storage', '.git', '__pycache__', '.pytest_cache', 'node_modules']
    
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Remove diretórios excluídos
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py') and file not in ['index_code.py', 'cli_query.py']:
                python_files.append(os.path.join(root, file))
    
    return python_files

def read_python_file(filepath: str) -> Dict:
    """Le um arquivo Python e extrai metadados."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extrair funcoes e classes
        lines = content.split('\n')
        functions = []
        classes = []
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('def '):
                func_name = line.strip().split('(')[0].replace('def ', '')
                functions.append({'name': func_name, 'line': i})
            elif line.strip().startswith('class '):
                class_name = line.strip().split('(')[0].replace('class ', '').split(':')[0]
                classes.append({'name': class_name, 'line': i})
        
        return {
            'filepath': filepath,
            'lines_of_code': len(lines),
            'functions': functions,
            'classes': classes,
            'size_bytes': len(content.encode('utf-8')),
            'first_lines': '\n'.join(lines[:10])  # Primeiras 10 linhas para contexto
        }
    except Exception as e:
        return {
            'filepath': filepath,
            'error': str(e)
        }

def run_indexing():
    """Indexa o codigo-fonte e salva em JSON (sem dependencias pesadas)."""
    
    print("[INDEXACAO] INICIANDO INDEXACAO DO CODIGO...")
    print(f"[INFO] Diretorio: {CODE_DIR}")
    
    # 1. Encontrar arquivos Python
    print("\n[PASSO 1] Procurando arquivos Python...")
    python_files = get_python_files(CODE_DIR)
    print(f"[OK] {len(python_files)} arquivos Python encontrados")
    
    # 2. Processar cada arquivo
    print("\n[PASSO 2] Indexando arquivos...")
    index_data = {
        'timestamp': str(__import__('datetime').datetime.now()),
        'total_files': len(python_files),
        'files': []
    }
    
    for i, filepath in enumerate(python_files, 1):
        print(f"   [{i}/{len(python_files)}] {filepath}")
        file_info = read_python_file(filepath)
        index_data['files'].append(file_info)
    
    # 3. Salvar indice em JSON
    print("\n[PASSO 3] Salvando indice em disco...")
    os.makedirs(PERSIST_DIR, exist_ok=True)
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    # Estatisticas
    total_functions = sum(len(f.get('functions', [])) for f in index_data['files'])
    total_classes = sum(len(f.get('classes', [])) for f in index_data['files'])
    total_lines = sum(f.get('lines_of_code', 0) for f in index_data['files'])
    
    print("-" * 50)
    print(f"[OK] INDEXACAO CONCLUIDA!")
    print(f"  - Arquivos indexados: {len(python_files)}")
    print(f"  - Funcoes encontradas: {total_functions}")
    print(f"  - Classes encontradas: {total_classes}")
    print(f"  - Total de linhas: {total_lines}")
    print(f"  - Indice salvo em: {INDEX_FILE}")
    print("-" * 50)

if __name__ == "__main__":
    try:
        run_indexing()
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
