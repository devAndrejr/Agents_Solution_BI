'''
Interface de Usuário (Frontend) para o Agent_BI, reescrita para ser um
cliente puro da API FastAPI.
'''
import streamlit as st
import requests
import uuid

# --- Configuração da Página ---
st.set_page_config(
    page_title="Agent_BI",
    page_icon="📊",
    layout="wide"
)
st.title("📊 Agent_BI - Assistente Inteligente")

# --- Constantes ---
API_URL = "http://127.0.0.1:8000/api/v1/query"

# --- Gerenciamento de Estado da Sessão ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Como posso ajudar você com seus dados hoje?"}]

# --- Funções de Interação com a API ---
def get_agent_response(user_query: str):
    '''Envia a query para a API FastAPI e retorna a resposta.'''
    try:
        payload = {
            "user_query": user_query,
            "session_id": st.session_state.session_id
        }
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()  # Lança exceção para status de erro HTTP
        return response.json().get("response", {})
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com o backend: {e}")
        return {"type": "error", "content": "Não foi possível conectar ao servidor do agente."}

# --- Renderização da Interface ---
# Exibe o histórico da conversa
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # O conteúdo agora é um dicionário com 'type' e 'content'
        response_data = msg.get("content")
        if isinstance(response_data, dict):
            response_type = response_data.get("type")
            content = response_data.get("content")
            
            if response_type == "chart":
                st.plotly_chart(content, use_container_width=True)
            elif response_type == "clarification":
                st.markdown(content.get("message"))
                # Renderiza botões para as opções de esclarecimento
                # Esta parte precisaria de uma lógica de callback mais complexa
                # para enviar a resposta do botão de volta para a API.
                # Por simplicidade, apenas exibimos as opções.
                for choice_type, choices in content.get("choices", {}).items():
                    st.write(f"**{choice_type.replace('_', ' ').title()}:**")
                    cols = st.columns(len(choices))
                    for i, choice in enumerate(choices):
                        if cols[i].button(choice):
                            # Em uma implementação real, este clique enviaria uma nova query
                            st.session_state.messages.append({"role": "user", "content": choice})
                            # Aqui, apenas adicionamos ao chat e rerodamos
                            st.rerun()

            else: # type 'data', 'text', 'error'
                st.write(content)
        else: # Formato antigo ou texto simples
            st.write(response_data)

# Input do usuário
if prompt := st.chat_input("Faça sua pergunta..."):
    # Adiciona e exibe a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Obtém e exibe a resposta do assistente
    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            agent_response = get_agent_response(prompt)
            
            # Adiciona a resposta completa ao histórico para renderização
            st.session_state.messages.append({"role": "assistant", "content": agent_response})
            
            # Renderiza a resposta imediatamente
            response_type = agent_response.get("type")
            content = agent_response.get("content")

            if response_type == "chart":
                st.plotly_chart(content, use_container_width=True)
            elif response_type == "clarification":
                st.markdown(content.get("message"))
                # Simplificado: Apenas mostra as opções, sem funcionalidade de clique aqui
                for choice_type, choices in content.get("choices", {}).items():
                    st.write(f"**{choice_type.replace('_', ' ').title()}:**")
                    for choice in choices:
                        st.button(choice, disabled=True) # Desabilitado para evitar loop
            else: # data, text, error
                st.write(content)