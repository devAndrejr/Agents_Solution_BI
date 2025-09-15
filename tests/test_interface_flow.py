"""
Teste para verificar o fluxo completo de perguntas e respostas na interface.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import requests
import json
from typing import Dict, Any

# Configurar logging para o teste
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterfaceFlowTester:
    """Testa o fluxo completo da interface."""

    def __init__(self, api_url: str = "http://127.0.0.1:8000"):
        self.api_url = api_url
        self.session_id = "test_session_123"

    def test_query_response_flow(self, user_query: str) -> Dict[str, Any]:
        """Testa uma query completa e verifica a resposta."""
        logger.info(f"🧪 TESTING QUERY: '{user_query}'")

        # Simular o que o frontend faz
        payload = {
            "user_query": user_query,
            "session_id": self.session_id
        }

        try:
            # Fazer request para a API
            response = requests.post(
                f"{self.api_url}/api/v1/query",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            agent_response = response.json()

            # Analisar a resposta
            response_type = agent_response.get("type", "unknown")
            content = agent_response.get("content")

            logger.info(f"✅ RESPONSE RECEIVED - Type: {response_type}")
            logger.info(f"📝 CONTENT LENGTH: {len(str(content)) if content else 0}")

            # Verificar se a estrutura está correta
            if response_type in ["chart", "data", "text", "clarification"]:
                logger.info("✅ RESPONSE STRUCTURE: Valid")
            else:
                logger.warning(f"⚠️ UNEXPECTED RESPONSE TYPE: {response_type}")

            return {
                "success": True,
                "user_query": user_query,
                "response_type": response_type,
                "has_content": content is not None,
                "content_length": len(str(content)) if content else 0,
                "full_response": agent_response
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ REQUEST ERROR: {e}")
            return {
                "success": False,
                "user_query": user_query,
                "error": str(e)
            }

    def test_multiple_queries(self):
        """Testa múltiplas queries para verificar o histórico."""
        test_queries = [
            "Olá, como você pode me ajudar?",
            "Quais são os 5 produtos mais vendidos?",
            "Gere um gráfico de vendas do produto 369947",
            "Mostre dados do segmento TECIDOS"
        ]

        results = []
        for query in test_queries:
            result = self.test_query_response_flow(query)
            results.append(result)

        # Verificar se todas as queries foram processadas
        successful_queries = [r for r in results if r.get("success")]
        logger.info(f"📊 SUMMARY: {len(successful_queries)}/{len(test_queries)} queries successful")

        return results

    def test_interface_simulation(self):
        """Simula o comportamento completo da interface Streamlit."""
        logger.info("🚀 STARTING INTERFACE SIMULATION")

        # Simular estado de sessão do Streamlit
        session_state = {
            "session_id": self.session_id,
            "messages": [
                {
                    "role": "assistant",
                    "content": {
                        "type": "text",
                        "content": "Olá! Como posso ajudar você com seus dados hoje?"
                    }
                }
            ]
        }

        test_queries = [
            "Quais produtos mais vendem?",
            "Gere um gráfico de vendas por categoria"
        ]

        for user_input in test_queries:
            logger.info(f"👤 USER INPUT: '{user_input}'")

            # Adicionar pergunta ao histórico (como faz o Streamlit)
            user_message = {
                "role": "user",
                "content": {
                    "type": "text",
                    "content": user_input
                }
            }
            session_state["messages"].append(user_message)

            # Fazer query para API
            result = self.test_query_response_flow(user_input)

            if result.get("success"):
                # Adicionar resposta ao histórico
                assistant_message = {
                    "role": "assistant",
                    "content": result["full_response"]
                }
                session_state["messages"].append(assistant_message)

                logger.info(f"📋 MESSAGE HISTORY LENGTH: {len(session_state['messages'])}")

        # Verificar histórico final
        user_messages = [msg for msg in session_state["messages"] if msg["role"] == "user"]
        assistant_messages = [msg for msg in session_state["messages"] if msg["role"] == "assistant"]

        logger.info(f"✅ FINAL HISTORY: {len(user_messages)} user messages, {len(assistant_messages)} assistant messages")

        # Verificar se as perguntas estão preservadas
        for i, msg in enumerate(user_messages):
            user_question = msg["content"]["content"]
            logger.info(f"📝 USER QUESTION {i+1}: '{user_question}'")

        return session_state

def main():
    """Executar testes."""
    print("🧪 Testing Interface Flow for Agent_BI")
    print("=" * 50)

    tester = InterfaceFlowTester()

    # Verificar se a API está rodando
    try:
        response = requests.get(f"{tester.api_url}/status", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print("❌ API not responding correctly")
            return
    except requests.exceptions.RequestException:
        print("❌ API is not running. Start the backend first with: python main.py")
        return

    # Executar testes
    print("\n1. Testing single query...")
    single_result = tester.test_query_response_flow("Quais são os produtos mais vendidos?")
    print(f"Single query result: {single_result.get('success')}")

    print("\n2. Testing multiple queries...")
    multiple_results = tester.test_multiple_queries()
    print(f"Multiple queries completed: {len(multiple_results)} total")

    print("\n3. Testing interface simulation...")
    final_state = tester.test_interface_simulation()
    print(f"Interface simulation completed. Final message count: {len(final_state['messages'])}")

    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()