"""
Script para verificar a saúde da interface e corrigir problemas comuns.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time
import subprocess
import logging
from typing import Dict, List, Tuple

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InterfaceHealthChecker:
    """Verificador de saúde da interface Agent_BI."""

    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:8501"
        self.issues_found = []
        self.fixes_applied = []

    def check_backend_health(self) -> bool:
        """Verifica se o backend está respondendo."""
        try:
            response = requests.get(f"{self.backend_url}/status", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Backend está rodando e respondendo")
                return True
            else:
                logger.error(f"❌ Backend respondeu com status {response.status_code}")
                self.issues_found.append(f"Backend status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ Backend não está rodando")
            self.issues_found.append("Backend não está acessível")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao verificar backend: {e}")
            self.issues_found.append(f"Erro backend: {e}")
            return False

    def check_frontend_health(self) -> bool:
        """Verifica se o frontend está respondendo."""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                logger.info("✅ Frontend (Streamlit) está rodando e respondendo")
                return True
            else:
                logger.error(f"❌ Frontend respondeu com status {response.status_code}")
                self.issues_found.append(f"Frontend status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ Frontend não está rodando")
            self.issues_found.append("Frontend não está acessível")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao verificar frontend: {e}")
            self.issues_found.append(f"Erro frontend: {e}")
            return False

    def test_query_flow(self) -> bool:
        """Testa o fluxo completo de uma query."""
        if not self.check_backend_health():
            return False

        try:
            payload = {
                "user_query": "Teste de conectividade",
                "session_id": "health_check_session"
            }

            logger.info("🧪 Testando fluxo de query...")
            response = requests.post(
                f"{self.backend_url}/api/v1/query",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                response_type = result.get("type", "unknown")
                logger.info(f"✅ Query flow funcionando - Tipo: {response_type}")
                return True
            else:
                logger.error(f"❌ Query flow falhou - Status: {response.status_code}")
                self.issues_found.append(f"Query flow error: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Erro no teste de query: {e}")
            self.issues_found.append(f"Query test error: {e}")
            return False

    def check_memory_usage(self) -> bool:
        """Verifica uso de memória."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            available_gb = memory.available / (1024**3)

            logger.info(f"💾 Memória: {memory_percent:.1f}% usado, {available_gb:.1f}GB disponível")

            if memory_percent > 90:
                logger.warning("⚠️ Uso de memória alto (>90%)")
                self.issues_found.append("Uso de memória alto")
                return False
            elif available_gb < 1:
                logger.warning("⚠️ Pouca memória disponível (<1GB)")
                self.issues_found.append("Pouca memória disponível")
                return False
            else:
                logger.info("✅ Uso de memória OK")
                return True

        except ImportError:
            logger.warning("⚠️ psutil não instalado - não foi possível verificar memória")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao verificar memória: {e}")
            return True

    def check_parquet_file(self) -> bool:
        """Verifica se o arquivo parquet existe e é acessível."""
        parquet_path = "data/parquet/admatao.parquet"

        if not os.path.exists(parquet_path):
            logger.error(f"❌ Arquivo parquet não encontrado: {parquet_path}")
            self.issues_found.append("Arquivo parquet não encontrado")
            return False

        try:
            import pandas as pd
            df = pd.read_parquet(parquet_path)
            logger.info(f"✅ Arquivo parquet OK - Shape: {df.shape}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao ler arquivo parquet: {e}")
            self.issues_found.append(f"Erro no parquet: {e}")
            return False

    def suggest_fixes(self) -> List[str]:
        """Sugere correções para os problemas encontrados."""
        suggestions = []

        if "Backend não está acessível" in self.issues_found:
            suggestions.append("▶️ Iniciar backend: python main.py")

        if "Frontend não está acessível" in self.issues_found:
            suggestions.append("▶️ Iniciar frontend: python -m streamlit run streamlit_app.py")

        if "Arquivo parquet não encontrado" in self.issues_found:
            suggestions.append("▶️ Verificar se o arquivo está em data/parquet/admatao.parquet")

        if "Uso de memória alto" in self.issues_found:
            suggestions.append("▶️ Fechar aplicações desnecessárias ou reiniciar o sistema")

        if any("Query" in issue for issue in self.issues_found):
            suggestions.append("▶️ Verificar logs em logs/errors/ para detalhes dos erros")

        return suggestions

    def run_full_check(self) -> Dict:
        """Executa verificação completa da interface."""
        logger.info("🔍 Iniciando verificação completa da interface...")

        results = {
            "backend_ok": self.check_backend_health(),
            "frontend_ok": self.check_frontend_health(),
            "query_flow_ok": False,
            "memory_ok": self.check_memory_usage(),
            "parquet_ok": self.check_parquet_file(),
            "issues": self.issues_found,
            "suggestions": []
        }

        # Só testa query se backend estiver OK
        if results["backend_ok"]:
            results["query_flow_ok"] = self.test_query_flow()

        results["suggestions"] = self.suggest_fixes()

        # Resumo final
        all_ok = all([
            results["backend_ok"],
            results["frontend_ok"],
            results["query_flow_ok"],
            results["memory_ok"],
            results["parquet_ok"]
        ])

        if all_ok:
            logger.info("🎉 Todos os componentes estão funcionando corretamente!")
        else:
            logger.warning(f"⚠️ {len(self.issues_found)} problemas encontrados")

        return results

def main():
    """Executar verificação de saúde."""
    print("🏥 Agent_BI - Verificação de Saúde da Interface")
    print("=" * 50)

    checker = InterfaceHealthChecker()
    results = checker.run_full_check()

    print("\n📊 RESUMO DOS RESULTADOS:")
    print("-" * 30)
    print(f"Backend:     {'✅' if results['backend_ok'] else '❌'}")
    print(f"Frontend:    {'✅' if results['frontend_ok'] else '❌'}")
    print(f"Query Flow:  {'✅' if results['query_flow_ok'] else '❌'}")
    print(f"Memória:     {'✅' if results['memory_ok'] else '❌'}")
    print(f"Arquivo:     {'✅' if results['parquet_ok'] else '❌'}")

    if results["issues"]:
        print(f"\n❌ PROBLEMAS ENCONTRADOS ({len(results['issues'])}):")
        for i, issue in enumerate(results["issues"], 1):
            print(f"  {i}. {issue}")

    if results["suggestions"]:
        print(f"\n💡 SUGESTÕES DE CORREÇÃO:")
        for suggestion in results["suggestions"]:
            print(f"  {suggestion}")

    print(f"\n🔗 URLs dos serviços:")
    print(f"  Backend:  http://localhost:8000")
    print(f"  Frontend: http://localhost:8501")

if __name__ == "__main__":
    main()