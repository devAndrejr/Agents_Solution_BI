import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import streamlit.components.v1 as components
import sys

from core import auth
from core.query_processor import QueryProcessor

audit_logger = logging.getLogger("audit")

# --- Constantes ---
from core.session_state import SESSION_STATE_KEYS
ROLES = {"ASSISTANT": "assistant", "USER": "user"}
PAGE_CONFIG = {
    "page_title": "Assistente de BI - Caçula",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# --- Configuração da Página e Estilos ---
st.set_page_config(**PAGE_CONFIG)

# Load CSS from external file for better organization
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def initialize_session_state():
    """Inicializa o estado da sessão se não existir."""
    if SESSION_STATE_KEYS["QUERY_PROCESSOR"] not in st.session_state:
        st.session_state[SESSION_STATE_KEYS["QUERY_PROCESSOR"]] = QueryProcessor()
    if SESSION_STATE_KEYS["MESSAGES"] not in st.session_state:
        st.session_state[SESSION_STATE_KEYS["MESSAGES"]] = [
            {
                "role": ROLES["ASSISTANT"],
                "output": "Olá! Como posso ajudar você hoje?",
            }
        ]
    if "dashboard_charts" not in st.session_state: # Adicionado para inicializar o dashboard_charts
        st.session_state.dashboard_charts = []


def handle_logout():
    """Limpa o estado da sessão e força o rerun para a tela de login."""
    username = st.session_state.get(SESSION_STATE_KEYS["USERNAME"], "N/A")
    audit_logger.info(f"Usuário {username} deslogado.")
    keys_to_clear = [
        SESSION_STATE_KEYS["AUTHENTICATED"],
        SESSION_STATE_KEYS["USERNAME"],
        SESSION_STATE_KEYS["ROLE"],
        SESSION_STATE_KEYS["LAST_LOGIN"],
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def show_bi_assistant():
    """Exibe a interface principal do assistente de BI."""
    st.markdown(
        "<h1 class='main-header'>📊 Assistente de BI Caçulinha</h1>",
        unsafe_allow_html=True,
    )
    
    

    # Exibir histórico de mensagens
    for message in st.session_state[SESSION_STATE_KEYS["MESSAGES"]]:
        with st.chat_message(message["role"]):
            output = message.get("output")
            if isinstance(output, pd.DataFrame):
                st.dataframe(output, use_container_width=True)
            elif isinstance(output, dict) and output.get("type") == "chart": # Para gráficos Plotly
                st.plotly_chart(output.get("output"), use_container_width=True)
            else: # Para texto, gráficos Plotly diretos ou outros tipos de dicionário inesperados
                if isinstance(output, go.Figure): # Se for um objeto Plotly Figure
                    st.plotly_chart(output, use_container_width=True)
                else: # Para texto ou outros tipos de dicionário inesperados
                    st.markdown(str(output or ""))

    # Exemplos de perguntas na barra lateral
    st.sidebar.markdown("### Exemplos de Perguntas:")
    st.sidebar.info("Qual o preço do produto 719445?")
    st.sidebar.info("Liste os produtos da categoria 'BRINQUEDOS'")
    st.sidebar.info("Mostre um gráfico de vendas para o produto 610403")

    # Entrada do usuário
    if prompt := st.chat_input("Faça uma pergunta sobre seus dados..."):
        # Input validation and sanitization
        if not prompt.strip(): # Check for empty or whitespace-only input
            st.warning("Por favor, digite uma pergunta válida.")
            return # Stop processing if input is empty

        if len(prompt) > 500: # Example: Limit input length to 500 characters
            st.warning("Sua pergunta é muito longa. Por favor, seja mais conciso (máximo 500 caracteres).")
            return # Stop processing if input is too long

        # Adicionar mensagem do usuário ao histórico e exibir
        st.session_state[SESSION_STATE_KEYS["MESSAGES"]].append(
            {"role": ROLES["USER"], "output": prompt}
        )
        with st.chat_message(ROLES["USER"]):
            st.markdown(prompt)

        # Processar a pergunta e obter a resposta
        with st.chat_message(ROLES["ASSISTANT"]):
            st.info("Aguarde enquanto o assistente processa sua solicitação...") # Added info message
            with st.spinner("O assistente de BI está pensando..."): # More generic spinner message
                query_processor = st.session_state[
                    SESSION_STATE_KEYS["QUERY_PROCESSOR"]
                ]
                response = query_processor.process_query(prompt)
                # st.write(response) # Removido para evitar exposição de dados

                # Adicionar resposta do assistente ao histórico e exibir
                st.session_state[SESSION_STATE_KEYS["MESSAGES"]].append(
                    {"role": ROLES["ASSISTANT"], "output": response["output"]}
                )
                if response["type"] == "dataframe":
                    st.dataframe(response["output"], use_container_width=True)
                elif response["type"] == "chart":
                    st.plotly_chart(response["output"], use_container_width=True)
                    
                    # Adicionar ao dashboard_charts
                    if "dashboard_charts" not in st.session_state:
                        st.session_state.dashboard_charts = []
                    
                    st.session_state.dashboard_charts.append({
                        "type": "chart", # Tipo agora é 'chart'
                        "output": response["output"], # Objeto Plotly direto
                        "title": f"Gráfico gerado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", # Título genérico
                        "query": prompt, # A consulta original
                        "timestamp": datetime.now().timestamp()
                    })
                    st.success("Gráfico adicionado ao Dashboard!")
                else:
                    if response["type"] == "text":
                        st.markdown(response["output"])
                    else: # Para qualquer outro tipo inesperado, exibe o dicionário completo para depuração
                        st.markdown(str(response))

    st.markdown(
        f"<div class='footer'>Desenvolvido para Análise de Dados Caçula © {datetime.now().year}</div>",
        unsafe_allow_html=True,
    )


def show_admin_dashboard():
    """Exibe o painel de administração para usuários com perfil 'admin'."""
    st.markdown(
        "<h1 class='main-header'>⚙️ Painel de Administração</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='sub-header'>Gerencie usuários, configurações e monitore o sistema.</p>",
        unsafe_allow_html=True,
    )
    st.subheader("Funcionalidades:")
    st.write("- Gerenciamento de usuários")
    st.write("- Visualização de logs")
    st.write("- Configurações do sistema")
    st.markdown(
        f"<div class='footer'>Desenvolvido para Análise de Dados Caçula © {datetime.now().year}</div>",
        unsafe_allow_html=True,
    )


import logging
import uuid
# import sentry_sdk
import os
from core.config.logging_config import setup_logging
from core.utils.context import correlation_id_var

logger = logging.getLogger(__name__)

def main():
    """Função principal que controla o fluxo da aplicação."""
    setup_logging()
    # sentry_dsn = os.getenv("SENTRY_DSN")
    # if sentry_dsn:
    #     sentry_sdk.init(
    #         dsn=sentry_dsn,
    #         traces_sample_rate=1.0,
    #     )

    # Set correlation id
    if 'correlation_id' not in st.session_state:
        st.session_state.correlation_id = str(uuid.uuid4())
    correlation_id_var.set(st.session_state.correlation_id)

    logger.info("Iniciando a aplicação Streamlit.")
    initialize_session_state()

    # --- Verificação de Autenticação e Sessão ---
    if not st.session_state.get(SESSION_STATE_KEYS["AUTHENTICATED"]):
        auth.login()
        st.stop()

    if auth.sessao_expirada():
        st.warning(
            "Sua sessão expirou por inatividade. Faça login novamente para continuar."
        )
        handle_logout()
        # A tela de login será exibida no próximo rerun após o st.stop()
        st.stop()


    # --- Barra Lateral e Logout ---
    username = st.session_state.get(SESSION_STATE_KEYS["USERNAME"])
    role = st.session_state.get(SESSION_STATE_KEYS["ROLE"])

    

    if username:
        st.sidebar.markdown(
            f"<span style='color:#2563EB;'>Bem-vindo, <b>{username}</b>!</span>",
            unsafe_allow_html=True,
        )
        st.sidebar.markdown("<hr>", unsafe_allow_html=True)
        if st.sidebar.button("Sair"):
            handle_logout()

    # --- Renderização do Conteúdo Principal ---
    show_bi_assistant()


if __name__ == "__main__":
    main()