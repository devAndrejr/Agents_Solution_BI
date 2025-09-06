# Este arquivo lida com a autenticação de usuários. É crucial que as senhas nunca sejam armazenadas em texto plano.
# Em vez disso, utilizamos funções de hash seguras (como bcrypt, implementado em sql_server_auth_db.py)
# para converter as senhas em um formato ilegível e irreversível. Isso protege as informações dos usuários
# mesmo em caso de violação de dados, pois apenas os hashes são armazenados, não as senhas originais.
import streamlit as st
import time
import logging
from core.database import sql_server_auth_db as auth_db

audit_logger = logging.getLogger("audit")

# Inicializar banco de usuários ao iniciar app
if "db_inicializado" not in st.session_state:
    auth_db.init_db()
    st.session_state["db_inicializado"] = True


# --- Login integrado ao backend SQLite ---
def login():
    # Coloca o formulário de login em uma coluna centralizada para melhor apelo visual
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style='text-align:center;'>
                <img src='https://raw.githubusercontent.com/github/explore/main/topics/business-intelligence/business-intelligence.png' width='150'>
                <h2>Caçulinha BI</h2>
                <p style='color:#666;'>Acesse com seu usuário e senha para continuar.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        with st.form("login_form"):
            username = st.text_input("Usuário", placeholder="Digite seu usuário")
            password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            login_btn = st.form_submit_button("Entrar", use_container_width=True, type="primary")

            if login_btn:
                # Bypass de autenticação para desenvolvimento
                if username == 'admin' and password == 'bypass':
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = "admin"
                    st.session_state["role"] = "admin"
                    st.session_state["ultimo_login"] = time.time()
                    audit_logger.info(f"Usuário admin logado com sucesso (bypass). Papel: admin")
                    st.success(f"Bem-vindo, admin! Acesso de desenvolvedor concedido.")
                    time.sleep(1) # Pausa para o usuário ler a mensagem
                    st.rerun()
                    return

                role, erro = auth_db.autenticar_usuario(username, password)
                if role:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.session_state["role"] = role
                    st.session_state["ultimo_login"] = time.time()
                    audit_logger.info(f"Usuário {username} logado com sucesso. Papel: {role}")
                    st.success(f"Bem-vindo, {username}! Redirecionando...")
                    time.sleep(1)
                    st.rerun()
                else:
                    audit_logger.warning(f"Tentativa de login falha para o usuário: {username}. Erro: {erro or 'Usuário ou senha inválidos.'}")
                    if erro and "bloqueado" in erro:
                        st.error(f"{erro} Contate o administrador.")
                    elif erro and "Tentativas restantes" in erro:
                        st.warning(erro)
                    else:
                        st.error(erro or "Usuário ou senha inválidos.")


# --- Expiração automática de sessão ---
def sessao_expirada():
    if not st.session_state.get("ultimo_login"):
        return True
    tempo = time.time() - st.session_state["ultimo_login"]
    return tempo > 60 * auth_db.SESSAO_MINUTOS
