"""
Authentication Module for Code Chat
Implements admin-only access control for RAG interface
"""

import streamlit as st
import hashlib
import os
from typing import Optional, Tuple

# ============================================================================
# ADMIN CREDENTIALS CONFIGURATION
# ============================================================================

def get_admin_password() -> str:
    """
    Get admin password from environment variable or use default.
    
    In production, use: 
    $env:ADMIN_PASSWORD='seu-password-seguro'
    
    Returns:
        str: Hashed password for comparison
    """
    # Tentar obter do ambiente, senão usar padrão
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    return hash_password(password)


def hash_password(password: str) -> str:
    """
    Hash a password using SHA256.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to verify
        hashed: Hashed password to compare against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return hash_password(password) == hashed


# ============================================================================
# AUTHENTICATION FUNCTIONS
# ============================================================================

def initialize_auth_state():
    """Initialize authentication state in session."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "admin_name" not in st.session_state:
        st.session_state.admin_name = None
    
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0


def is_authenticated() -> bool:
    """
    Check if user is authenticated as admin.
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    return st.session_state.get("authenticated", False)


def get_admin_name() -> Optional[str]:
    """
    Get authenticated admin name.
    
    Returns:
        str: Admin name if authenticated, None otherwise
    """
    return st.session_state.get("admin_name", None)


def login_admin(username: str, password: str) -> Tuple[bool, str]:
    """
    Authenticate admin login.
    
    Args:
        username: Admin username
        password: Admin password
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    # Simple validation - in production use database
    valid_username = "admin"
    valid_password_hash = get_admin_password()
    
    # Check attempts
    if st.session_state.login_attempts >= 5:
        return False, "❌ Muitas tentativas falhas. Tente novamente em 1 hora."
    
    # Verify credentials
    if username == valid_username and verify_password(password, valid_password_hash):
        st.session_state.authenticated = True
        st.session_state.admin_name = username
        st.session_state.login_attempts = 0
        return True, "✅ Login realizado com sucesso!"
    else:
        st.session_state.login_attempts += 1
        remaining = 5 - st.session_state.login_attempts
        return False, f"❌ Credenciais inválidas. Tentativas restantes: {remaining}"


def logout_admin():
    """Logout authenticated admin."""
    st.session_state.authenticated = False
    st.session_state.admin_name = None
    st.session_state.login_attempts = 0


# ============================================================================
# LOGIN UI COMPONENT
# ============================================================================

def show_login_page():
    """Display login page for admin authentication."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🔐 Acesso Restrito - Code Chat")
        st.markdown("---")
        
        st.info(
            "🔒 **Apenas administradores têm acesso ao Code Chat**\n\n"
            "Por favor, faça login com suas credenciais de admin."
        )
        
        st.markdown("### Login")
        
        # Login form
        username = st.text_input(
            "👤 Usuário",
            placeholder="Digite seu usuário admin",
            help="Usuário padrão: admin"
        )
        
        password = st.text_input(
            "🔑 Senha",
            type="password",
            placeholder="Digite sua senha",
            help="Configure ADMIN_PASSWORD na variável de ambiente"
        )
        
        col_login, col_info = st.columns([2, 1])
        
        with col_login:
            if st.button("🔓 Fazer Login", use_container_width=True, type="primary"):
                if username and password:
                    success, message = login_admin(username, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("⚠️ Por favor, preencha usuário e senha")
        
        with col_info:
            with st.expander("ℹ️ Padrão"):
                st.caption("**Padrão:**\n\nuser: `admin`\n\npass: `admin123`")
        
        st.markdown("---")
        
        # Information about changing password
        with st.expander("🔐 Alterar Senha"):
            st.markdown(
                """
                Para alterar a senha padrão:
                
                **No PowerShell:**
                ```powershell
                $env:ADMIN_PASSWORD='sua-nova-senha-segura'
                streamlit run streamlit_app.py
                ```
                
                **No arquivo .env:**
                ```
                ADMIN_PASSWORD=sua-nova-senha-segura
                ```
                
                **Recomendações:**
                - Use senhas com 12+ caracteres
                - Combine maiúsculas, minúsculas, números e símbolos
                - Não use senhas fáceis de adivinhar
                """
            )


def show_protected_content(content_func):
    """
    Wrapper to show protected content only if authenticated.
    
    Args:
        content_func: Function that renders the protected content
    """
    initialize_auth_state()
    
    if not is_authenticated():
        show_login_page()
        st.stop()
    
    # Show authenticated content
    content_func()


# ============================================================================
# ADMIN LOGOUT SIDEBAR BUTTON
# ============================================================================

def show_logout_button():
    """Show logout button in sidebar for authenticated users."""
    if is_authenticated():
        with st.sidebar:
            st.markdown("---")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.caption(f"👤 **Conectado como:** `{get_admin_name()}`")
            
            with col2:
                if st.button("🚪 Logout", use_container_width=True):
                    logout_admin()
                    st.rerun()
            
            st.markdown("---")
