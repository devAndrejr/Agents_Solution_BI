# Streamlit + shadcn-ui (Elwynn Chen) — Shell pronto para agente Caçulinha
# -------------------------------------------------------------
# Este app entrega:
# - Layout com abas (Chat / Visões / Diagnóstico)
# - Chat em balão com quick actions (chips)
# - Exibição de gráficos Plotly e tabelas lado a lado em Cards
# - Toasts/Callouts (quando disponível via streamlit-shadcn-ui)
# - Erros amigáveis e loaders
# - Leitura de variáveis de ambiente (.env)
# - Pontos de integração para: agente supervisor, SQL Server e geração de gráficos
# -------------------------------------------------------------

import os
import json
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.express as px

# Tenta usar shadcn-ui; se não existir, o app segue com Streamlit puro
try:
    import streamlit_shadcn_ui as ui  # pip install streamlit-shadcn-ui
    HAS_SHADCN = True
except Exception:
    HAS_SHADCN = False

# -------------------------------------------------------------
# Configuração básica
# -------------------------------------------------------------
st.set_page_config(
    page_title="Caçulinha BI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS simples p/ balões de chat e cards
st.markdown(
    """
    <style>
      .chat-row { display: flex; margin: 6px 0; }
      .chat-left { justify-content: flex-start; }
      .chat-right { justify-content: flex-end; }
      .bubble { max-width: 900px; padding: 10px 14px; border-radius: 14px; line-height: 1.4; }
      .bubble-user { background: #0ea5e9; color: white; border-top-right-radius: 6px; }
      .bubble-bot { background: #111827; color: #e5e7eb; border-top-left-radius: 6px; }
      .badge { padding: 4px 10px; border-radius: 9999px; border: 1px solid #e5e7eb; font-size: 12px; }
      .chip-row { display:flex; gap: 6px; flex-wrap: wrap; margin: 8px 0 2px 0; }
      .chip { padding: 6px 10px; border: 1px solid #d1d5db; border-radius: 9999px; cursor: pointer; }
      .kbd { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; background:#111827; color:#f9fafb; padding:1px 6px; border-radius:6px; font-size:12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# Utilidades
# -------------------------------------------------------------
from dataclasses import dataclass

@dataclass
class AgentResult:
    text: str
    df: pd.DataFrame | None = None
    fig: object | None = None
    tips: list[str] | None = None


def load_env():
    """Carrega variáveis de ambiente se `.env` estiver presente."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass


load_env()

# Placeholders de conexão (troque para seu conector real)
SQL_SERVER_DSN = os.getenv("SQLSERVER_DSN", "SQLSERVER_DSN_EXEMPLO")
DEFAULT_SCHEMA = os.getenv("DEFAULT_SCHEMA", "dbo")

# -------------------------------------------------------------
# Estado
# -------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Oi! Eu sou o Caçulinha. Pergunte sobre rupturas, vendas por categoria ou estoque parado."}
    ]

if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------------------------------------------
# Funções de agente (stub) — PLUGUE seu agente aqui
# -------------------------------------------------------------

def run_agent(prompt: str) -> AgentResult:
    """Substitua pela sua chamada ao agente supervisor (LangGraph/LLM).
    O retorno contempla texto + opcionalmente gráfico/tabela + dicas.
    """
    # Exemplos de roteamento simples por intenção
    p = prompt.lower()

    # Exemplo: "vendas por categoria no mês 09"
    if "vendas" in p and "categoria" in p:
        df = pd.DataFrame({
            "categoria": ["Bebidas", "Higiene", "Mercearia"],
            "vendas": [154000, 121000, 98000],
        })
        fig = px.bar(df, x="categoria", y="vendas", title="Vendas por Categoria (Exemplo)")
        tips = [
            "Top 1 contribui 45–55% do total — avalie preço médio e ruptura.",
            "Cruze vendas vs. margem para ranking por rentabilidade.",
            "Aplique curva ABC por loja para calibrar sortimento.",
        ]
        text = "Conferi as vendas por categoria. Veja o gráfico e as 3 quick-wins ao lado."
        return AgentResult(text=text, df=df, fig=fig, tips=tips)

    # Exemplo: "produtos com ruptura (últimos 7 dias)"
    if "ruptur" in p:
        df = pd.DataFrame({
            "produto": ["Arroz 5kg", "Detergente 500ml", "Biscoito 120g"],
            "ruptura_%": [12.3, 8.4, 6.1],
        })
        fig = px.bar(df, x="produto", y="ruptura_%", title="Ruptura por Produto (Exemplo)")
        tips = [
            "Ative reposição priorizada p/ ruptura > 8%.",
            "Valide saldo em estoque vs. PDV e lead time do fornecedor.",
            "Alerte OPCOM para auditoria física nas top 5 rupturas.",
        ]
        text = "Mapeei as maiores rupturas. Sugiro priorizar os itens >8% hoje."
        return AgentResult(text=text, df=df, fig=fig, tips=tips)

    # Exemplo: "estoque parado > 60 dias"
    if "estoque" in p and ("parado" in p or "obsoleto" in p):
        df = pd.DataFrame({
            "produto": ["Refri Lata 269ml", "Shampoo 300ml", "Granola 1kg"],
            "dias_sem_venda": [75, 68, 92],
        })
        fig = px.bar(df, x="produto", y="dias_sem_venda", title="Estoque Parado (Exemplo)")
        tips = [
            "Rodar queima com ponta de gôndola e preço psicológico.",
            "Avaliar transferência entre lojas (balanço de estoque).",
            "Acordo com fornecedor para devolução/bonificação parcial.",
        ]
        text = "Encontrei itens com >60 dias sem venda. Três alavancas sugeridas ao lado."
        return AgentResult(text=text, df=df, fig=fig, tips=tips)

    # Default: só responde texto
    return AgentResult(text="Beleza! Preciso de mais contexto — posso abrir vendas por categoria, rupturas ou estoque parado. O que prefere?")


# -------------------------------------------------------------
# Sidebar — Config/Atalhos
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Configuração")
    st.write("DSN SQL Server:", f"`{SQL_SERVER_DSN}`")
    st.write("Schema padrão:", f"`{DEFAULT_SCHEMA}`")

    if HAS_SHADCN:
        ui.switch(key="darkmode", label="Modo escuro (tema do sistema)", value=True)
        ui.badges(badges=[{"text": "stable", "variant": "secondary"}, {"text": "v1", "variant": "outline"}],
                  className="mb-2")
        ui.button("Documentação interna", key="btn_docs", variant="secondary")
    else:
        st.info("shadcn-ui não encontrado. Rode: pip install streamlit-shadcn-ui")

# -------------------------------------------------------------
# Header
# -------------------------------------------------------------
col_l, col_r = st.columns([0.75, 0.25])
with col_l:
    st.title("Caçulinha BI — Operação Varejo")
with col_r:
    if HAS_SHADCN:
        ui.button("🧪 Rodar smoke test", key="btn_smoke")
    else:
        st.button("🧪 Rodar smoke test")

# -------------------------------------------------------------
# Abas
# -------------------------------------------------------------
if HAS_SHADCN:
    active_tab = ui.tabs(options=["Chat", "Visões", "Diagnóstico"], default_value="Chat", key="tabs_main")
else:
    t1, t2, t3 = st.tabs(["Chat", "Visões", "Diagnóstico"])
    active_tab = None

# -------------------------------------------------------------
# Conteúdo: Chat
# -------------------------------------------------------------

def render_chat():
    # Histórico
    for m in st.session_state.messages:
        role = m.get("role", "assistant")
        content = m.get("content", "")
        row_class = "chat-right" if role == "user" else "chat-left"
        bubble_class = "bubble-user" if role == "user" else "bubble-bot"
        st.markdown(
            f'<div class="chat-row {row_class}"><div class="bubble {bubble_class}">{content}</div></div>',
            unsafe_allow_html=True,
        )

    # Chips de atalho
    st.markdown("<div class='chip-row'>", unsafe_allow_html=True)
    chips = [
        "Rupturas (últimos 7 dias)",
        "Vendas por categoria no mês atual",
        "Estoque parado > 60 dias",
    ]
    chip_cols = st.columns(len(chips))
    for i, label in enumerate(chips):
        if chip_cols[i].button(label, key=f"chip_{i}"):
            st.session_state["prompt_input"] = label
    st.markdown("</div>", unsafe_allow_html=True)

    # Input
    with st.container():
        c1, c2 = st.columns([0.85, 0.15])
        prompt = c1.text_input("Digite sua pergunta", key="prompt_input", placeholder="Ex.: Vendas por categoria no mês 09")
        send = c2.button("Enviar", use_container_width=True)

    # Envio
    if send and prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Consultando o Caçulinha…"):
            try:
                res = run_agent(prompt)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
                # Renderiza imediatamente (além de registrar no histórico)
                st.markdown(
                    f'<div class="chat-row chat-left"><div class="bubble bubble-bot">{res.text}</div></div>',
                    unsafe_allow_html=True,
                )
                # Se houver insights/tips, mostra ao lado
                if res.tips:
                    st.markdown("**Dicas de negócio (auto)**")
                    for tip in res.tips:
                        st.markdown(f"- {tip}")
                # Se tiver dados/gráfico, empacota para a aba Visões
                if res.df is not None or res.fig is not None:
                    st.session_state.history.append({
                        "when": datetime.now().isoformat(timespec="seconds"),
                        "prompt": prompt,
                        "df": res.df,
                        "fig": res.fig,
                        "note": res.text,
                    })
                if HAS_SHADCN:
                    ui.toast("Resposta gerada", description="O Caçulinha concluiu a tarefa.")
            except Exception as e:
                if HAS_SHADCN:
                    ui.alert_dialog(title="Falha ao responder", description=str(e))
                st.error("Deu ruim, mas a mensagem está clara: " + str(e))


# -------------------------------------------------------------
# Conteúdo: Visões (gráficos/tabelas)
# -------------------------------------------------------------

def render_views():
    st.subheader("Visões salvas da sessão")
    if not st.session_state.history:
        st.info("Nenhuma visão ainda. Gere algo no chat e volta aqui.")
        return

    for i, item in enumerate(reversed(st.session_state.history)):
        st.markdown(f"**Consulta:** `{item['prompt']}` · _{item['when']}_")
        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            if item.get("fig") is not None:
                st.plotly_chart(item["fig"], use_container_width=True)
        with col2:
            if item.get("df") is not None:
                st.dataframe(item["df"], use_container_width=True, height=320)
        if note := item.get("note"):
            st.caption("Nota do agente: " + note)
        st.divider()


# -------------------------------------------------------------
# Conteúdo: Diagnóstico (logs simples)
# -------------------------------------------------------------

def render_diag():
    st.subheader("Diagnóstico rápido")
    st.json(
        {
            "sqlserver_dsn": SQL_SERVER_DSN,
            "default_schema": DEFAULT_SCHEMA,
            "shadcn_ui": HAS_SHADCN,
            "visoes": len(st.session_state.history),
            "msgs": len(st.session_state.messages),
        }
    )
    st.caption("Use esta aba para mostrar SQL executado, tempos de resposta, contadores, etc.")


# -------------------------------------------------------------
# Router das abas
# -------------------------------------------------------------
if HAS_SHADCN:
    if active_tab == "Chat":
        render_chat()
    elif active_tab == "Visões":
        render_views()
    else:
        render_diag()
else:
    with t1:
        render_chat()
    with t2:
        render_views()
    with t3:
        render_diag()

# -------------------------------------------------------------
# Como integrar:
# - Substitua run_agent() pelo seu pipeline real (LangGraph + SQL + Plotly).
# - Para SQL Server, injete um executor que receba a string SQL e retorne DataFrame.
# - Para mensagens, mantenha st.session_state.messages (é o histórico do chat).
# - Para dicas de negócio, preencha o campo tips no retorno do agente.
# -------------------------------------------------------------
