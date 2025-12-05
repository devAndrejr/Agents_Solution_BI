"""
Módulo para pages/10_🤖_Gemini_Playground.py. Define componentes da interface de utilizador (UI).
"""

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from datetime import datetime
import logging
import json
import random

# Configurar logging
logger = logging.getLogger(__name__)

# --- Verificação de Autenticação e Permissão ---
if st.session_state.get("authenticated") and st.session_state.get("role") == "admin":
    # --- Configuração da Página ---
    st.set_page_config(
        page_title="Gemini Playground",
        page_icon="🤖",
        layout="wide"
    )

    st.markdown(
        "<h1 class='main-header'>🤖 Gemini Playground</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='sub-header'>Teste e experimente com o modelo Gemini 2.5 Flash.</p>",
        unsafe_allow_html=True,
    )

    # Importar componentes necessários
    try:
        from core.llm_adapter import GeminiLLMAdapter
        from core.config.safe_settings import get_safe_settings

        settings = get_safe_settings()

        # Verificar se a API key está configurada
        if not settings.GEMINI_API_KEY:
            st.error("❌ API Key do Gemini não configurada. Configure GEMINI_API_KEY nas variáveis de ambiente.")
            st.stop()

        # Usar @st.cache_resource para evitar erro de serialização do OpenAI client
        @st.cache_resource(show_spinner="Inicializando Gemini...")
        def load_gemini_adapter():
            gemini_model = getattr(settings, 'GEMINI_MODEL_NAME', settings.LLM_MODEL_NAME)
            return GeminiLLMAdapter(
                api_key=settings.GEMINI_API_KEY,
                model_name=gemini_model,
                enable_cache=True
            )

        gemini = load_gemini_adapter()

        # Layout em colunas
        col1, col2 = st.columns([2, 1])

        with col2:
            st.subheader("⚙️ Configurações")

            if st.button("🔄 Recarregar Configuração da API", use_container_width=True, help="Clique aqui se você atualizou sua chave de API no arquivo .env para forçar o recarregamento."):
                from core.config.safe_settings import reset_safe_settings_cache
                # Limpa o cache de settings para forçar a releitura do .env
                reset_safe_settings_cache()
                # Limpa o cache do adapter para que ele seja recriado com a nova chave
                st.cache_resource.clear()
                st.success("Configuração da API recarregada. Tente seu prompt novamente.")
                st.rerun()
            
            st.markdown("---")

            # Parâmetros do modelo
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                help="Controla a criatividade das respostas. Valores mais baixos são mais determinísticos."
            )

            max_tokens = st.slider(
                "Max Tokens",
                min_value=256,
                max_value=8192,
                value=2048,
                step=256,
                help="Número máximo de tokens na resposta (Gemini conta prompt + resposta)."
            )

            # Aviso se max_tokens muito baixo
            if max_tokens < 512:
                st.warning("⚠️ Valor muito baixo! Respostas podem ser cortadas. Recomendado: ≥ 1024 tokens.")

            json_mode = st.checkbox(
                "JSON Mode",
                value=False,
                help="Força o modelo a retornar respostas em formato JSON."
            )

            stream_mode = st.checkbox(
                "Stream Mode",
                value=False,
                help="Exibe as respostas em tempo real (streaming)."
            )

            # Informações do modelo
            st.markdown("---")
            st.subheader("📊 Informações")
            st.info(f"**Modelo:** {gemini.model_name}")

            # Estatísticas do cache
            cache_stats = gemini.get_cache_stats()
            if cache_stats.get("cache_enabled"):
                st.metric("Cache Hits", cache_stats.get("hits", 0))
                st.metric("Cache Misses", cache_stats.get("misses", 0))
                hit_rate = cache_stats.get("hit_rate", 0) * 100
                st.metric("Taxa de Acerto", f"{hit_rate:.1f}%")
            else:
                st.warning("Cache desabilitado")

            # Botão para limpar histórico
            st.markdown("---")
            if st.button("🗑️ Limpar Histórico", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        with col1:
            st.subheader("💬 Chat")

            # Inicializar histórico de chat
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []

            # Container para o histórico de mensagens
            chat_container = st.container()

            # Exibir histórico
            with chat_container:
                for message in st.session_state.chat_history:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            # Input do usuário
            user_input = st.chat_input("Digite sua mensagem...")

            if user_input:
                # Adicionar mensagem do usuário ao histórico
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input
                })

                # Preparar mensagens para o modelo (incluindo a mensagem do usuário)
                messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.chat_history
                ]

                # Obter resposta do modelo
                try:
                    if stream_mode:
                        # Modo streaming
                        with st.spinner("Gerando resposta..."):
                            stream = gemini.get_completion(
                                messages=messages,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                json_mode=json_mode,
                                stream=True
                            )

                            full_response = ""
                            for chunk in stream:
                                full_response += chunk

                            response_content = full_response

                    else:
                        # Modo normal
                        with st.spinner("Gerando resposta..."):
                            response = gemini.get_completion(
                                messages=messages,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                json_mode=json_mode,
                                stream=False
                            )

                        if "error" in response:
                            error_msg = f"❌ Erro: {response['error']}"
                            if response.get("fallback_activated"):
                                error_msg += f"\n\n🔄 Fallback sugerido: {response.get('retry_with', 'N/A')}"
                            response_content = error_msg
                        else:
                            response_content = response.get("content", "")
                            if not response_content:
                                response_content = "❌ Resposta vazia recebida do modelo."

                except Exception as e:
                    error_msg = f"❌ Erro ao gerar resposta: {str(e)}"
                    response_content = error_msg
                    logger.error(f"Erro no playground: {e}", exc_info=True)

                # Adicionar resposta ao histórico
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response_content
                })

                # Forçar rerun para exibir a conversa atualizada
                st.rerun()

            # Exemplos de prompts
            st.markdown("---")
            st.subheader("💡 Exemplos de Prompts")

            # Inicializar variável de exemplo se não existir
            if 'selected_example' not in st.session_state:
                st.session_state.selected_example = ""

            # Pool de exemplos variados para cada categoria
            exemplos_analise = [
                "Explique como fazer uma análise exploratória de dados de vendas.",
                "Quais são as principais métricas para analisar performance de vendas?",
                "Como identificar tendências sazonais em dados de vendas?",
                "Descreva técnicas para detectar outliers em dados de estoque.",
                "Como analisar a correlação entre campanhas de marketing e vendas?"
            ]

            exemplos_sql = [
                "Crie uma query SQL para calcular o total de vendas por categoria nos últimos 30 dias.",
                "Escreva uma query SQL para encontrar os 10 produtos mais vendidos por filial.",
                "Gere uma query SQL para calcular a taxa de crescimento mensal de vendas.",
                "Crie uma query SQL para identificar produtos com baixo giro de estoque.",
                "Escreva uma query SQL para analisar vendas por dia da semana."
            ]

            exemplos_python = [
                "Escreva código Python para criar um gráfico de barras com matplotlib.",
                "Crie código Python para gerar um dashboard interativo com Plotly.",
                "Escreva código Python para análise de séries temporais com pandas.",
                "Gere código Python para criar um heatmap de correlação com seaborn.",
                "Crie código Python para fazer clustering de produtos com scikit-learn."
            ]

            # Callbacks para os botões de exemplo (melhor prática do Streamlit)
            def select_example(categoria):
                if categoria == "analise":
                    exemplo = random.choice(exemplos_analise)
                elif categoria == "sql":
                    exemplo = random.choice(exemplos_sql)
                elif categoria == "python":
                    exemplo = random.choice(exemplos_python)
                else:
                    exemplo = ""

                st.session_state.selected_example = exemplo

            col_ex1, col_ex2, col_ex3 = st.columns(3)

            with col_ex1:
                st.button(
                    "📝 Análise de Dados",
                    use_container_width=True,
                    on_click=select_example,
                    args=["analise"]
                )

            with col_ex2:
                st.button(
                    "🔍 SQL Query",
                    use_container_width=True,
                    on_click=select_example,
                    args=["sql"]
                )

            with col_ex3:
                st.button(
                    "📊 Python Code",
                    use_container_width=True,
                    on_click=select_example,
                    args=["python"]
                )

            # Mostrar campo editável se um exemplo foi selecionado
            if st.session_state.selected_example:
                st.markdown("---")
                st.info("✏️ Edite o prompt abaixo antes de enviar, se desejar:")

                edited_prompt = st.text_area(
                    "Prompt:",
                    value=st.session_state.selected_example,
                    height=100,
                    key="editable_example"
                )

                col_send, col_cancel = st.columns([1, 1])

                with col_send:
                    if st.button("📤 Enviar", use_container_width=True, type="primary"):
                        if edited_prompt.strip():
                            # Adicionar ao histórico
                            st.session_state.chat_history.append({
                                "role": "user",
                                "content": edited_prompt
                            })

                            # Preparar mensagens para o modelo
                            messages = [
                                {"role": msg["role"], "content": msg["content"]}
                                for msg in st.session_state.chat_history
                            ]

                            # Obter resposta do modelo
                            try:
                                if stream_mode:
                                    # Modo streaming
                                    with st.spinner("Gerando resposta..."):
                                        stream = gemini.get_completion(
                                            messages=messages,
                                            temperature=temperature,
                                            max_tokens=max_tokens,
                                            json_mode=json_mode,
                                            stream=True
                                        )

                                        full_response = ""
                                        for chunk in stream:
                                            full_response += chunk

                                        response_content = full_response

                                else:
                                    # Modo normal
                                    with st.spinner("Gerando resposta..."):
                                        response = gemini.get_completion(
                                            messages=messages,
                                            temperature=temperature,
                                            max_tokens=max_tokens,
                                            json_mode=json_mode,
                                            stream=False
                                        )

                                    if "error" in response:
                                        error_msg = f"❌ Erro: {response['error']}"
                                        if response.get("fallback_activated"):
                                            error_msg += f"\n\n🔄 Fallback sugerido: {response.get('retry_with', 'N/A')}"
                                        response_content = error_msg
                                    else:
                                        response_content = response.get("content", "")
                                        if not response_content:
                                            response_content = "❌ Resposta vazia recebida do modelo."

                            except Exception as e:
                                error_msg = f"❌ Erro ao gerar resposta: {str(e)}"
                                response_content = error_msg
                                logger.error(f"Erro no playground ao processar exemplo: {e}", exc_info=True)

                            # Adicionar resposta ao histórico
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": response_content
                            })

                            # Limpar exemplo selecionado
                            st.session_state.selected_example = ""

                            # Recarregar para mostrar a conversa atualizada
                            st.rerun()

                with col_cancel:
                    def clear_example():
                        st.session_state.selected_example = ""

                    st.button(
                        "❌ Cancelar",
                        use_container_width=True,
                        on_click=clear_example
                    )

    except ImportError as e:
        st.error(f"❌ Erro ao importar componentes necessários: {e}")
        st.info("Verifique se todas as dependências estão instaladas.")
        logger.error(f"Erro de importação no Gemini Playground: {e}")
    except Exception as e:
        st.error(f"❌ Erro inesperado: {e}")
        logger.error(f"Erro no Gemini Playground: {e}", exc_info=True)

    st.markdown(
        f"<div class='footer'>Desenvolvido para Análise de Dados Caçula © {datetime.now().year}</div>",
        unsafe_allow_html=True,
    )

# Se não for admin, mostra uma mensagem de erro e oculta o conteúdo.
elif st.session_state.get("authenticated"):
    st.error("❌ Acesso negado. Você não tem permissão para acessar esta página.")
    st.info("ℹ️ Esta página é exclusiva para administradores.")
    st.stop()

# Se não estiver logado, redireciona para o login
else:
    st.error("❌ Acesso negado. Por favor, faça o login na página principal para acessar esta área.")
    st.stop()
