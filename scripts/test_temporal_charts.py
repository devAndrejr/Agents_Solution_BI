"""
Script para testar a geração de gráficos temporais.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time
from typing import List, Dict

class TemporalChartsTestRunner:
    """Testador específico para gráficos temporais."""

    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.test_results = []

    def test_query(self, query: str, expected_type: str = "chart") -> Dict:
        """Testa uma query específica."""
        print(f"🧪 Testando: '{query}'")

        payload = {
            "user_query": query,
            "session_id": f"test_temporal_{int(time.time())}"
        }

        try:
            response = requests.post(
                f"{self.api_url}/api/v1/query",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                response_type = result.get("type", "unknown")

                success = response_type == expected_type
                status = "✅ SUCESSO" if success else f"❌ FALHA (esperado: {expected_type}, recebido: {response_type})"

                print(f"   {status}")
                if response_type == "chart":
                    print("   📈 Gráfico gerado com sucesso!")
                elif response_type == "data":
                    content = result.get("content", [])
                    print(f"   📊 Dados retornados: {len(content)} registros")
                else:
                    print(f"   ℹ️ Tipo: {response_type}")

                return {
                    "query": query,
                    "success": success,
                    "response_type": response_type,
                    "expected_type": expected_type,
                    "full_response": result
                }

            else:
                print(f"   ❌ ERRO HTTP: {response.status_code}")
                return {
                    "query": query,
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_type": "error"
                }

        except Exception as e:
            print(f"   ❌ EXCEÇÃO: {str(e)}")
            return {
                "query": query,
                "success": False,
                "error": str(e),
                "response_type": "error"
            }

    def run_temporal_tests(self) -> List[Dict]:
        """Executa testes específicos para análises temporais."""
        print("🕒 TESTES DE ANÁLISES TEMPORAIS")
        print("=" * 50)

        temporal_queries = [
            # Testes de evolução temporal
            "Gere um gráfico da evolução de vendas do produto 369947",
            "Mostre a tendência de vendas nos últimos 6 meses",
            "Evolução mensal de vendas do produto 369947",
            "Histórico de vendas dos últimos 12 meses",

            # Testes de períodos específicos
            "Vendas nos últimos 3 meses do produto 369947",
            "Gráfico temporal de vendas do segmento TECIDOS",

            # Testes para comparação (devem funcionar)
            "Gere um gráfico de vendas do produto 369947",  # Sem temporal
            "Top 10 produtos mais vendidos",  # Sem temporal
        ]

        expected_types = [
            "chart",  # evolução de vendas
            "chart",  # tendência últimos 6 meses
            "chart",  # evolução mensal
            "chart",  # histórico 12 meses
            "chart",  # últimos 3 meses
            "chart",  # gráfico temporal segmento
            "chart",  # vendas produto (pode ser temporal ou não)
            "data",   # top 10 produtos (lista/dados)
        ]

        results = []
        for query, expected in zip(temporal_queries, expected_types):
            result = self.test_query(query, expected)
            results.append(result)
            print()  # Linha em branco entre testes
            time.sleep(2)  # Pausa entre requests

        return results

    def analyze_results(self, results: List[Dict]):
        """Analisa os resultados dos testes."""
        print("📊 ANÁLISE DOS RESULTADOS")
        print("=" * 50)

        total_tests = len(results)
        successful_tests = len([r for r in results if r.get("success")])
        chart_responses = len([r for r in results if r.get("response_type") == "chart"])

        print(f"Total de testes: {total_tests}")
        print(f"Sucessos: {successful_tests}")
        print(f"Taxa de sucesso: {successful_tests/total_tests*100:.1f}%")
        print(f"Gráficos gerados: {chart_responses}")

        print("\n🔍 DETALHES POR TESTE:")
        print("-" * 30)

        for i, result in enumerate(results, 1):
            query = result["query"]
            success = result.get("success", False)
            response_type = result.get("response_type", "unknown")

            status_icon = "✅" if success else "❌"
            print(f"{i:2d}. {status_icon} {response_type:8s} | {query[:50]}...")

        # Identificar problemas específicos
        failed_temporals = []
        for result in results:
            if not result.get("success") and any(word in result["query"].lower()
                                               for word in ["evolução", "tendência", "histórico", "últimos", "temporal"]):
                failed_temporals.append(result["query"])

        if failed_temporals:
            print(f"\n⚠️ ANÁLISES TEMPORAIS QUE FALHARAM ({len(failed_temporals)}):")
            for query in failed_temporals:
                print(f"   - {query}")
        else:
            print("\n🎉 TODAS AS ANÁLISES TEMPORAIS FUNCIONARAM!")

        return {
            "total": total_tests,
            "successful": successful_tests,
            "success_rate": successful_tests/total_tests*100,
            "charts_generated": chart_responses,
            "failed_temporals": failed_temporals
        }

def main():
    """Executar testes de gráficos temporais."""
    print("📈 Agent_BI - Teste de Gráficos Temporais")
    print("=" * 50)

    # Verificar se a API está rodando
    try:
        response = requests.get("http://localhost:8000/status", timeout=5)
        if response.status_code != 200:
            print("❌ API não está respondendo corretamente")
            return
        print("✅ API está rodando")
    except:
        print("❌ API não está acessível. Inicie o backend: python main.py")
        return

    # Executar testes
    tester = TemporalChartsTestRunner()
    results = tester.run_temporal_tests()
    summary = tester.analyze_results(results)

    # Recomendações
    print("\n💡 RECOMENDAÇÕES:")
    if summary["success_rate"] < 80:
        print("   - Revisar prompts de classificação de intenção")
        print("   - Verificar geração de código para análises temporais")
        print("   - Testar com dados reais menores")
    else:
        print("   - Sistema funcionando bem para análises temporais!")

    if summary["failed_temporals"]:
        print("   - Investigar falhas específicas nos logs")
        print("   - Melhorar detecção de palavras-chave temporais")

    print(f"\n🎯 RESULTADO FINAL: {summary['success_rate']:.1f}% de sucesso")

if __name__ == "__main__":
    main()