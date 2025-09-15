'''
Interface de Usuário (Frontend) para o Agent_BI.
'''
import streamlit as st
import requests
import uuid
import pandas as pd
from core.auth import login, sessao_expirada

# --- Autenticação ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated or sessao_expirada():
    st.session_state.authenticated = False
    login()
else:
    # --- Configuração da Página ---
    st.set_page_config(page_title="Agent_BI", page_icon="📊", layout="wide")
    st.title("📊 Agent_BI - Assistente Inteligente")

    # --- Logout Button ---
    with st.sidebar:
        st.write(f"Bem-vindo, {st.session_state.get('username', '')}!")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.role = ""
            # Clear chat history on logout
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": {
                        "type": "text",
                        "content": "Você foi desconectado. Faça login para continuar."
                    }
                }
            ]
            st.rerun()


    # --- Constantes e Estado da Sessão ---
    API_URL = "http://127.0.0.1:8000/api/v1/query"

    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": {
                    "type": "text",
                    "content": "Olá! Como posso ajudar você com seus dados hoje?"
                }
            }
        ]

    # --- Funções de Interação ---
    def query_backend(user_input: str):
        '''Envia a query para a API e lida com a resposta.'''
        # 📝 GARANTIR que a pergunta do usuário seja sempre preservada
        user_message = {"role": "user", "content": {"type": "text", "content": user_input}}
        st.session_state.messages.append(user_message)

        # 🔍 LOG da pergunta (removido print para evitar problemas de encoding)
        # print(f"USER QUESTION ADDED: '{user_input}' - Total messages: {len(st.session_state.messages)}")

        with st.spinner("O agente está a pensar..."):
            try:
                payload = {"user_query": user_input, "session_id": st.session_state.session_id}
                response = requests.post(API_URL, json=payload, timeout=120)
                response.raise_for_status()
                agent_response = response.json()

                # ✅ GARANTIR estrutura correta da resposta
                assistant_message = {"role": "assistant", "content": agent_response}
                st.session_state.messages.append(assistant_message)

                # 🔍 LOG da resposta (removido print para evitar problemas de encoding)
                # print(f"AGENT RESPONSE ADDED: Type={agent_response.get('type', 'unknown')} - Total messages: {len(st.session_state.messages)}")

            except requests.exceptions.Timeout:
                error_content = {"type": "error", "content": "Tempo limite esgotado. O servidor pode estar sobrecarregado. Tente novamente."}
                st.session_state.messages.append({"role": "assistant", "content": error_content})
            except requests.exceptions.ConnectionError:
                error_content = {"type": "error", "content": "Não foi possível conectar ao servidor. Verifique se o backend está rodando."}
                st.session_state.messages.append({"role": "assistant", "content": error_content})
            except requests.exceptions.RequestException as e:
                error_content = {"type": "error", "content": f"Erro na comunicação com o servidor: {str(e)}"}
                st.session_state.messages.append({"role": "assistant", "content": error_content})

        st.rerun()

    # --- Renderização da Interface ---
    # 🔍 DEBUG: Mostrar histórico de mensagens na sidebar (apenas para desenvolvimento)
    with st.sidebar:
        st.write(f"**Total de mensagens:** {len(st.session_state.messages)}")
        if st.checkbox("Mostrar histórico debug"):
            for i, msg in enumerate(st.session_state.messages):
                st.write(f"**{i+1}. {msg['role'].title()}:**")
                content_preview = str(msg.get('content', {}))[:100] + "..." if len(str(msg.get('content', {}))) > 100 else str(msg.get('content', {}))
                st.write(f"{content_preview}")

    # 💬 RENDERIZAR histórico de conversas
    for i, msg in enumerate(st.session_state.messages):
        try:
            with st.chat_message(msg["role"]):
                response_data = msg.get("content", {})

                # ✅ Garantir que response_data seja um dicionário
                if not isinstance(response_data, dict):
                    response_data = {"type": "text", "content": str(response_data)}

                response_type = response_data.get("type", "text")
                content = response_data.get("content", "Conteúdo não disponível")

            # 🔍 DEBUG: Log de renderização (removido print para evitar problemas)
            # if msg["role"] == "user":
            #     print(f"RENDERING USER MSG {i+1}: '{content}'")
            # else:
            #     print(f"RENDERING ASSISTANT MSG {i+1}: Type={response_type}")
            
            # 📈 RENDERIZAR GRÁFICOS
            if response_type == "chart":
                import json
                import plotly.graph_objects as go

                # 📝 Mostrar contexto da pergunta que gerou o gráfico
                user_query = response_data.get("user_query")
                if user_query:
                    st.caption(f"📝 Pergunta: {user_query}")

                try:
                    if isinstance(content, str):
                        # Se content é string JSON, parse para objeto
                        chart_data = json.loads(content)
                    else:
                        # Se content já é dict, usa diretamente
                        chart_data = content

                    # Cria figura Plotly a partir do JSON
                    fig = go.Figure(chart_data)
                    st.plotly_chart(fig, use_container_width=True)
                    st.success("✅ Gráfico gerado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao renderizar gráfico: {e}")
                    st.write("Dados do gráfico:", content)
            elif response_type == "data" and isinstance(content, list):
                # 📝 Mostrar contexto da pergunta que gerou os dados
                user_query = response_data.get("user_query")
                if user_query:
                    st.caption(f"📝 Pergunta: {user_query}")

                if content:
                    st.dataframe(pd.DataFrame(content))
                    st.info(f"📊 {len(content)} registros encontrados")
                else:
                    st.warning("⚠️ Nenhum dado encontrado para a consulta.")
            elif response_type == "clarification":
                st.markdown(content.get("message"))
                choices = content.get("choices", {})
                for choice_category, choice_list in choices.items():
                    for choice in choice_list:
                        if st.button(choice, key=f"btn_{choice}_{uuid.uuid4()}"):
                            query_backend(choice)
            else:
                # 📝 Para respostas de texto, também mostrar contexto se disponível
                user_query = response_data.get("user_query")
                if user_query and msg["role"] == "assistant":
                    st.caption(f"📝 Pergunta: {user_query}")

                st.write(content)

        except Exception as e:
            # ❌ Tratamento de erro na renderização
            st.error(f"Erro ao renderizar mensagem {i+1}: {str(e)}")
            st.write(f"Dados da mensagem: {msg}")

    if prompt := st.chat_input("Faça sua pergunta..."):
        query_backend(prompt)
