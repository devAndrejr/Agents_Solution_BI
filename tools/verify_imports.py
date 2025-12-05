"""Verifica importação de módulos críticos e imprime versão/erro.

Rode com o Python do venv: `venv\Scripts\python.exe tools\verify_imports.py`
"""
modules = [
    'plotly',
    'plotly.graph_objects',
    'dask',
    'dask.dataframe',
    'pyodbc',
    'openai',
    'langchain_core',
    'langgraph',
    'numpy',
    'pandas',
]

import importlib
import sys

results = []
for m in modules:
    try:
        mod = importlib.import_module(m)
        ver = getattr(mod, '__version__', None)
        results.append((m, 'OK', ver))
    except Exception as e:
        results.append((m, 'ERROR', str(e)))

print('Import verification results:')
for m, status, info in results:
    print(f'{m:25} | {status:5} | {info}')

sys.exit(0 if all(s=='OK' for _,s,_ in results) else 2)
