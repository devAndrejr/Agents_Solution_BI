#!/usr/bin/env python
"""Script de teste para validar 1_💻_Code_Chat.py"""

import ast
import glob
import sys
from pathlib import Path

def test_syntax():
    """Validar sintaxe Python"""
    print("[TESTE 1] Validação de Sintaxe Python")
    print("-" * 50)
    
    files = glob.glob("pages/*Code_Chat*.py")
    if not files:
        print("✗ Arquivo não encontrado")
        return False
    
    file_path = files[0]
    print(f"Arquivo encontrado: {file_path}")
    
    try:
        with open(file_path, encoding='utf-8') as f:
            code = f.read()
        
        ast.parse(code)
        print("✓ Sintaxe Python válida")
        print(f"✓ Tamanho: {len(code)} caracteres")
        print(f"✓ Linhas: {len(code.splitlines())}")
        return True
    except SyntaxError as e:
        print(f"✗ Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False


def test_imports():
    """Validar imports necessários"""
    print("\n[TESTE 2] Validação de Imports")
    print("-" * 50)
    
    required_imports = {
        'streamlit': 'st',
        'os': 'os',
        'json': 'json',
        'pathlib': 'Path',
        'typing': 'Optional, Any, Dict, List',
    }
    
    try:
        import streamlit
        import os
        import json
        from pathlib import Path
        from typing import Optional, Any, Dict, List
        
        print("✓ Todos os imports estão disponíveis:")
        for module, symbols in required_imports.items():
            print(f"  ✓ {module} ({symbols})")
        return True
    except ImportError as e:
        print(f"✗ Import faltando: {e}")
        return False


def test_structure():
    """Validar estrutura do código"""
    print("\n[TESTE 3] Validação de Estrutura")
    print("-" * 50)
    
    files = glob.glob("pages/*Code_Chat*.py")
    if not files:
        print("✗ Arquivo não encontrado")
        return False
    
    file_path = files[0]
    
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'st.set_page_config': content.count('st.set_page_config'),
            '@st.cache_resource': content.count('@st.cache_resource'),
            'def setup_rag_engine': content.count('def setup_rag_engine'),
            'class CodeQueryEngine': content.count('class CodeQueryEngine'),
            'st.session_state': content.count('st.session_state'),
            '"rag_messages"': content.count('"rag_messages"'),
            'st.chat_input': content.count('st.chat_input'),
            'query_engine.query': content.count('query_engine.query'),
            'st.spinner': content.count('st.spinner'),
            'st.title': content.count('st.title'),
            '💻': content.count('💻'),
        }
        
        all_valid = True
        for check, count in checks.items():
            status = "✓" if count > 0 else "✗"
            print(f"{status} {check}: {count} ocorrência(s)")
            if count == 0:
                all_valid = False
        
        return all_valid
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False


def test_index_json():
    """Validar índice JSON gerado"""
    print("\n[TESTE 4] Validação do Índice JSON")
    print("-" * 50)
    
    try:
        import json
        from pathlib import Path
        
        index_file = Path("./storage/code_index.json")
        
        if not index_file.exists():
            print(f"⚠ Arquivo de índice não encontrado: {index_file.absolute()}")
            print("  Execute 'python index_code.py' para gerar o índice")
            return True  # Não é erro crítico
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        total_files = len(index_data.get('files', []))
        timestamp = index_data.get('timestamp', 'unknown')
        
        print(f"✓ Índice JSON válido")
        print(f"✓ Arquivos indexados: {total_files}")
        print(f"✓ Timestamp: {timestamp}")
        
        return True
    except json.JSONDecodeError as e:
        print(f"✗ JSON inválido: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False


def main():
    """Executar todos os testes"""
    print("=" * 50)
    print("TESTES: 1_💻_Code_Chat.py")
    print("=" * 50)
    
    results = {
        'Sintaxe': test_syntax(),
        'Imports': test_imports(),
        'Estrutura': test_structure(),
        'Índice JSON': test_index_json(),
    }
    
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for r in results.values() if r)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} testes passaram")
    
    if total_passed == total_tests:
        print("\n✓ Todos os testes passaram com sucesso!")
        return 0
    else:
        print(f"\n✗ {total_tests - total_passed} teste(s) falharam")
        return 1


if __name__ == "__main__":
    sys.exit(main())
