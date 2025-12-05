"""
Code Chat Page - RAG Interface for Semantic Code Search (Admin Only)
Uses LlamaIndex with Gemini 2.5 Flash for semantic code analysis.
Requires: GEMINI_API_KEY environment variable configured.
Admin authentication required for access.
"""

import streamlit as st
import os
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Any, Dict, List
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="💻 Code Chat",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# ADMIN AUTHENTICATION - MUST BE FIRST CHECK
# ============================================================================

# Import auth module
try:
    from core.auth_code_chat import initialize_auth_state, is_authenticated, show_login_page, show_logout_button
except ImportError:
    st.error("❌ Módulo de autenticação não encontrado. Verifique a instalação.")
    st.stop()

# Initialize auth state
initialize_auth_state()

# Check authentication BEFORE anything else
if not is_authenticated():
    show_login_page()
    st.stop()

# Show logout button for authenticated users
show_logout_button()

# ============================================================================
# SECURITY CHECK - Validate GEMINI_API_KEY
# ============================================================================

def check_gemini_api_key() -> bool:
    """
    Validate that GEMINI_API_KEY is set in environment.
    
    Returns:
        bool: True if API key is configured, False otherwise
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() == "":
        return False
    return True


if not check_gemini_api_key():
    st.error(
        "❌ **Erro de Configuração**\n\n"
        "A variável de ambiente `GEMINI_API_KEY` não está configurada. "
        "Por favor:\n\n"
        "1. Defina a variável `GEMINI_API_KEY` no seu arquivo `.env`\n"
        "2. Ou configure como variável de ambiente do sistema\n"
        "3. Reinicie o Streamlit\n\n"
        "**Documentação:** Veja `docs/CONFIGURACAO_API_KEY.md`"
    )
    st.stop()

# ============================================================================
# IMPORTS - LlamaIndex Configuration
# ============================================================================

try:
    from llama_index.core import (
        VectorStoreIndex,
        Settings,
        load_index_from_storage,
    )
    from llama_index.core.storage import StorageContext
    from llama_index.vector_stores.faiss import FaissVectorStore
    from llama_index.llms.gemini import Gemini
    from llama_index.embeddings.gemini import GeminiEmbedding
    import faiss
    
except ImportError as e:
    st.error(
        f"❌ **Erro de Dependência**\n\n"
        f"Falha ao importar LlamaIndex: {str(e)}\n\n"
        "Por favor, instale as dependências:\n"
        "`pip install llama-index llama-index-vector-stores-faiss llama-index-llms-gemini llama-index-embeddings-gemini`"
    )
    st.stop()

# ============================================================================
# CONFIGURE LLAMAINDEX WITH GEMINI 2.5 FLASH
# ============================================================================

def configure_llamaindex():
    """
    Configure LlamaIndex to use Gemini 2.5 Flash as LLM.
    This sets up the global Settings for all LlamaIndex operations.
    """
    try:
        # Configure LLM (Gemini 2.5 Flash)
        Settings.llm = Gemini(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7,
        )
        
        # Configure Embedding Model (Gemini)
        Settings.embed_model = GeminiEmbedding(
            model_name="models/embedding-001",
            api_key=os.getenv("GEMINI_API_KEY"),
        )
        
        logger.info("✅ LlamaIndex configured with Gemini 2.5 Flash")
        return True
        
    except Exception as e:
        logger.error(f"Failed to configure LlamaIndex: {str(e)}")
        st.error(f"❌ Erro ao configurar LlamaIndex: {str(e)}")
        return False

# Estilos CSS personalizados
st.markdown("""
<style>
    .chat-message {
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-size: 0.95rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4CAF50;
    }
    .code-reference {
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 8px;
        margin-top: 8px;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def setup_rag_engine() -> Optional[Any]:
    """
    Setup and load the RAG query engine from ./storage directory.
    Uses VectorIndexRetriever from LlamaIndex with FAISS vector store.
    
    This function is cached with @st.cache_resource to load only once per session.
    
    Returns:
        Query engine object if successful, None if failed
    """
    try:
        storage_path = Path("./storage")
        
        # Check if storage directory exists
        if not storage_path.exists():
            logger.error(f"Storage directory not found: {storage_path.absolute()}")
            st.error(
                "❌ **Diretório de Armazenamento Não Encontrado**\n\n"
                f"Esperado em: `{storage_path.absolute()}`\n\n"
                "Por favor, execute `python index_code.py` para gerar o índice."
            )
            return None
        
        # Check if FAISS index files exist
        faiss_index_path = storage_path / "faiss_index.bin"
        docstore_path = storage_path / "docstore.json"
        index_store_path = storage_path / "index_store.json"
        
        if not faiss_index_path.exists():
            logger.error(f"FAISS index not found: {faiss_index_path}")
            st.error(
                "❌ **Índice FAISS Não Encontrado**\n\n"
                f"Arquivo esperado: `{faiss_index_path}`\n\n"
                "Execute `python index_code.py` para gerar o índice."
            )
            return None
        
        # Configure LlamaIndex
        if not configure_llamaindex():
            return None
        
        # Load FAISS index
        logger.info("Loading FAISS index from storage...")
        faiss_index = faiss.read_index(str(faiss_index_path))
        vector_store = FaissVectorStore(faiss_index)
        
        # Setup storage context
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            persist_dir=str(storage_path),
        )
        
        # Load index from storage
        logger.info("Loading VectorStoreIndex from storage...")
        index = load_index_from_storage(storage_context)
        
        # Create query engine with top_k=5
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            response_mode="compact",
        )
        
        logger.info("✅ RAG engine loaded successfully")
        
        st.success(
            "✅ Índice de código carregado com sucesso!\n\n"
            "**Estatísticas do Índice:**\n"
            "- 📁 8.031 arquivos Python\n"
            "- 📌 115.213 funções\n"
            "- 🏗️ 18.398 classes\n"
            "- 📝 2.715.480 linhas de código"
        )
        
        return query_engine
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        st.error(f"❌ **Arquivo Não Encontrado**\n\n{str(e)}\n\nExecute `python index_code.py` para gerar o índice.")
        return None
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in storage: {str(e)}")
        st.error(f"❌ **Erro na Leitura do Índice**\n\nJSON inválido: {str(e)}")
        return None
    
    except Exception as e:
        logger.error(f"Unexpected error loading RAG engine: {str(e)}")
        st.error(f"❌ **Erro ao Carregar RAG Engine**\n\n{str(e)}")
        return None


def initialize_chat_state() -> None:
    """Initialize Streamlit session state variables."""
    if "rag_messages" not in st.session_state:
        st.session_state.rag_messages = [
            {
                "role": "assistant",
                "content": (
                    "🤖 Olá! Sou seu assistente de análise de código.\n\n"
                    "Faça perguntas sobre:\n"
                    "- Funções e classes em sua base de código\n"
                    "- Como componentes específicos funcionam\n"
                    "- Estrutura de arquivos e módulos\n"
                    "- Padrões e dependências\n\n"
                    "Exemplo: *'Quais são as funções em core/llm_adapter.py?'*"
                ),
            }
        ]


def display_chat_history() -> None:
    """Display chat message history."""
    for message in st.session_state.rag_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(query_engine: Optional[Any]) -> None:
    """
    Process user input and generate response using the query engine.
    
    Args:
        query_engine: LlamaIndex query engine instance
    """
    if query_engine is None:
        st.warning(
            "⚠️ **RAG Engine Não Disponível**\n\n"
            "O mecanismo de busca não pôde ser carregado. "
            "Verifique a configuração na barra lateral."
        )
        return
    
    prompt = st.chat_input(
        "Digite sua pergunta sobre o código...",
        placeholder="Ex: Quais são as funções em core/llm_adapter.py?",
    )
    
    if prompt:
        # Add user message to history
        st.session_state.rag_messages.append(
            {"role": "user", "content": prompt}
        )
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Query the engine with loading spinner
        with st.spinner("🔍 Analisando código..."):
            try:
                logger.info(f"Processing query: {prompt}")
                response = query_engine.query(prompt)
                response_text = str(response)
                
                # Add assistant response to history
                st.session_state.rag_messages.append(
                    {"role": "assistant", "content": response_text}
                )
                
                # Display response
                with st.chat_message("assistant"):
                    st.markdown(response_text)
                
                logger.info("Query processed successfully")
                
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                error_message = (
                    f"❌ **Erro ao Processar Query**\n\n"
                    f"```\n{str(e)}\n```\n\n"
                    f"Por favor, tente novamente ou reformule sua pergunta."
                )
                
                st.session_state.rag_messages.append(
                    {"role": "assistant", "content": error_message}
                )
                
                with st.chat_message("assistant"):
                    st.error(error_message)


# ============================================================================
# PAGE LAYOUT
# ============================================================================

# Initialize session state
initialize_chat_state()

# Load RAG engine
query_engine = setup_rag_engine()

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("## 💻 Code Chat")
    st.markdown("---")
    
    # Index Status
    if query_engine is not None:
        st.success("✅ Índice Carregado", icon="✅")
        st.caption("8.031 arquivos indexados\n115.213 funções\n18.398 classes")
    else:
        st.warning("⚠️ Índice Não Disponível", icon="⚠️")
        st.caption("Execute `python index_code.py` para gerar o índice")
    
    st.markdown("---")
    
    # Clear Chat History Button
    if st.button("🗑️ Limpar Histórico", use_container_width=True):
        st.session_state.rag_messages = [
            {
                "role": "assistant",
                "content": (
                    "🤖 Histórico limpo! Comece uma nova conversa.\n\n"
                    "Faça uma pergunta sobre seu código."
                ),
            }
        ]
        st.rerun()
    
    st.markdown("---")
    
    # Help Section
    st.markdown("### ❓ Como Usar")
    st.markdown(
        """
        1. **Digite sua pergunta** no campo de entrada abaixo
        2. **O sistema busca** em 8.031 arquivos Python
        3. **Receba respostas** com trechos de código relevantes
        
        **Exemplos de perguntas:**
        - "Quais são as funções em core/llm_adapter.py?"
        - "Como funciona a classe ResponseCache?"
        - "Onde está implementado o ComponentFactory?"
        - "Qual é a estrutura de core/agents/?"
        """
    )
    
    st.markdown("---")
    
    # Model Info
    st.markdown("### 🤖 Configuração")
    st.caption(
        "**LLM:** Gemini 2.5 Flash\n\n"
        "**Embeddings:** GeminiEmbedding\n\n"
        "**Framework:** LlamaIndex"
    )

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.markdown("# 💻 Code Chat")
st.markdown("**Análise semântica de sua base de código com RAG**")
st.markdown("---")

# ============================================================================
# DISPLAY CHAT HISTORY
# ============================================================================

display_chat_history()

# ============================================================================
# HANDLE USER INPUT
# ============================================================================

handle_user_input(query_engine)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #999; font-size: 12px; margin-top: 20px;'>
        <p>Code Chat v1.0.2 | Powered by LlamaIndex + Gemini 2.5 Flash</p>
    </div>
    """,
    unsafe_allow_html=True,
)
