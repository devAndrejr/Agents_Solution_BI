import streamlit as st
import os
import time
import pandas as pd
import requests
from sqlalchemy import create_engine

from core.database import sql_server_auth_db as auth_db

st.markdown("<h1 class='main-header'>Monitoramento do Sistema</h1>", unsafe_allow_html=True)
st.markdown("<div class='info-box'>Acompanhe os logs do sistema e o status dos principais serviços.</div>", unsafe_allow_html=True)

# --- LOGS DO SISTEMA ---
st.markdown("### Logs do Sistema")
log_dir = os.path.join(os.getcwd(), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_files = [f for f in os.listdir(log_dir) if f.endswith(".log")]
if not log_files:
    st.warning("Nenhum arquivo de log encontrado.")
else:
    selected_log = st.selectbox("Selecione o arquivo de log", log_files)
    keyword = st.text_input("Filtrar por palavra-chave (opcional)")
    log_level = st.selectbox("Filtrar por nível", ["Todos", "INFO", "WARNING", "ERROR", "DEBUG"])
    log_path = os.path.join(log_dir, selected_log)
    log_lines = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if keyword and keyword.lower() not in line.lower():
                    continue
                if log_level != "Todos" and log_level not in line:
                    continue
                log_lines.append(line.strip())
    st.write(f"Total de linhas exibidas: {len(log_lines)}")
    st.dataframe(pd.DataFrame(log_lines, columns=["Log"]), use_container_width=True)

# --- STATUS DOS SERVIÇOS ---
st.markdown("### Status dos Serviços")
status_data = []
# Checagem da API
api_url = "http://localhost:5000/api/chat"  # ajuste se necessário
api_status = "-"
api_time = "-"
try:
    start = time.time()
    resp = requests.post(api_url, json={"message": "ping"}, timeout=3)
    api_time = f"{(time.time() - start)*1000:.0f} ms"
    if resp.status_code == 200:
        api_status = "OK"
    else:
        api_status = f"FALHA ({resp.status_code})"
except Exception as e:
    api_status = f"FALHA ({str(e)[:30]})"
status_data.append({"Serviço": "API", "Status": api_status, "Tempo": api_time})
# Checagem do Banco de Dados
db_status = "-"
db_time = "-"
try:
    from core.config.config import DB_CONNECTION_STRING

    start = time.time()
    engine = create_engine(DB_CONNECTION_STRING)
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    db_time = f"{(time.time() - start)*1000:.0f} ms"
    db_status = "OK"
except Exception as e:
    db_status = f"FALHA ({str(e)[:30]})"
status_data.append({"Serviço": "Banco de Dados", "Status": db_status, "Tempo": db_time})
# Checagem do LLM (OpenAI)
llm_status = "-"
llm_time = "-"
try:
    import openai

    from core.utils.openai_config import OPENAI_API_KEY

    openai.api_key = OPENAI_API_KEY
    start = time.time()
    openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=1,
        request_timeout=3,
    )
    llm_time = f"{(time.time() - start)*1000:.0f} ms"
    llm_status = "OK"
except Exception as e:
    llm_status = f"FALHA ({str(e)[:30]})"
status_data.append({"Serviço": "LLM (OpenAI)", "Status": llm_status, "Tempo": llm_time})
st.dataframe(pd.DataFrame(status_data), use_container_width=True)

# --- Função para admins aprovarem redefinição de senha ---
def painel_aprovacao_redefinicao():
    st.markdown("<h3>Solicitações de Redefinição de Senha</h3>", unsafe_allow_html=True)
    import sqlite3

    conn = sqlite3.connect(auth_db.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username FROM usuarios WHERE redefinir_solicitado=1 AND redefinir_aprovado=0")
    pendentes = [row[0] for row in c.fetchall()]
    if not pendentes:
        st.info("Nenhuma solicitação pendente.")
    else:
        for user in pendentes:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"Usuário: {user}")
            with col2:
                if st.button(f"Aprovar {user}"):
                    auth_db.aprovar_redefinicao(user)
                    st.success(f"Solicitação de {user} aprovada!")
                    st.rerun()
    conn.close()

# --- Função para usuário redefinir senha após aprovação ---
def tela_redefinir_senha():
    st.markdown("<h3>Redefinir Senha</h3>", unsafe_allow_html=True)
    st.info("Sua solicitação foi aprovada. Defina uma nova senha para continuar.")
    username = st.session_state.get("username")
    nova = st.text_input("Nova senha", type="password")
    nova2 = st.text_input("Confirme a nova senha", type="password")
    if st.button("Redefinir senha", use_container_width=True, help="Salvar nova senha"):
        if not nova or not nova2:
            st.warning("Preencha ambos os campos.")
        elif nova != nova2:
            st.error("As senhas não coincidem.")
        elif len(nova) < 6:
            st.warning("A senha deve ter pelo menos 6 caracteres.")
        else:
            try:
                auth_db.redefinir_senha(username, nova)
                st.success("Senha redefinida com sucesso! Você será redirecionado para o login.")
                time.sleep(2)
                for k in ["authenticated", "username", "role", "ultimo_login"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()
            except Exception as e:
                st.error(str(e))

# --- Checagem para exibir tela de redefinição após aprovação ---
def checar_redefinicao_aprovada():
    import sqlite3

    username = st.session_state.get("username")
    if not username:
        return False
    conn = sqlite3.connect(auth_db.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT redefinir_aprovado FROM usuarios WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return bool(row and row[0])

# --- Após login, checar se usuário deve redefinir senha ---
if st.session_state.get("authenticated") and checar_redefinicao_aprovada():
    tela_redefinir_senha()
    st.stop()

# --- Aba Monitoramento: admins podem aprovar redefinições ---
elif st.session_state.get("role") == "admin":
    painel_aprovacao_redefinicao()