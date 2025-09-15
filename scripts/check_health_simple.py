"""
Script simples para verificar a saude da interface sem emojis.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time

def check_backend():
    """Verifica se o backend esta rodando."""
    try:
        response = requests.get("http://localhost:8000/status", timeout=5)
        if response.status_code == 200:
            print("Backend: OK")
            return True
        else:
            print(f"Backend: ERRO (status {response.status_code})")
            return False
    except:
        print("Backend: NAO ACESSIVEL")
        return False

def check_frontend():
    """Verifica se o frontend esta rodando."""
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("Frontend: OK")
            return True
        else:
            print(f"Frontend: ERRO (status {response.status_code})")
            return False
    except:
        print("Frontend: NAO ACESSIVEL")
        return False

def test_query():
    """Testa uma query simples."""
    try:
        payload = {
            "user_query": "Teste de conectividade",
            "session_id": "health_check"
        }

        response = requests.post(
            "http://localhost:8000/api/v1/query",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"Query Test: OK (tipo: {result.get('type', 'unknown')})")
            return True
        else:
            print(f"Query Test: ERRO (status {response.status_code})")
            return False
    except Exception as e:
        print(f"Query Test: ERRO ({str(e)})")
        return False

def check_parquet():
    """Verifica arquivo parquet."""
    parquet_path = "data/parquet/admatao.parquet"

    if not os.path.exists(parquet_path):
        print("Arquivo Parquet: NAO ENCONTRADO")
        return False

    try:
        import pandas as pd
        df = pd.read_parquet(parquet_path)
        print(f"Arquivo Parquet: OK ({df.shape[0]} linhas, {df.shape[1]} colunas)")
        return True
    except Exception as e:
        print(f"Arquivo Parquet: ERRO ({str(e)})")
        return False

def main():
    print("Agent_BI - Verificacao de Saude")
    print("=" * 40)

    backend_ok = check_backend()
    frontend_ok = check_frontend()
    parquet_ok = check_parquet()

    query_ok = False
    if backend_ok:
        query_ok = test_query()
    else:
        print("Query Test: PULADO (backend nao acessivel)")

    print("\n" + "=" * 40)
    all_ok = backend_ok and frontend_ok and query_ok and parquet_ok

    if all_ok:
        print("RESULTADO: TODOS OS COMPONENTES OK!")
    else:
        print("RESULTADO: ALGUNS PROBLEMAS ENCONTRADOS")

        if not backend_ok:
            print("  > Iniciar backend: python main.py")
        if not frontend_ok:
            print("  > Iniciar frontend: python -m streamlit run streamlit_app.py")
        if not parquet_ok:
            print("  > Verificar arquivo em data/parquet/admatao.parquet")

    print("\nURLs:")
    print("  Backend:  http://localhost:8000")
    print("  Frontend: http://localhost:8501")

if __name__ == "__main__":
    main()