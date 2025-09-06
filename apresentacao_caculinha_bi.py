# Create a Streamlit presentation app as a single Python file and save it for download

app_code = r'''
# Caçulinha BI — Apresentação Executiva (em Streamlit)
# ----------------------------------------------------
# Como rodar:
#   streamlit run apresentacao_caculinha_bi.py
#
# Dependências:
#   pip install streamlit plotly pandas python-dotenv

import os
from datetime import datetime

import streamlit as st
import plotly.express as px
import pandas as pd

# --------- Config Básico ---------
st.set_page_config(
    page_title="Caçulinha BI — Apresentação",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------- Estado ---------
if "slide" not in st.session_state:
    st.session_state.slide = 0

# --------- Dados para gráficos de exemplo ---------
df_vendas = pd.DataFrame({
    "Categoria": ["Bebidas", "Higiene", "Mercearia", "Frios", "Limpeza"],
    "Vendas": [154000, 121000, 98000, 76000, 54000]
})
fig_vendas = px.bar(df_vendas, x="Categoria", y="Vendas", title="Vendas por Categoria (Exemplo)")

df_ruptura = pd.DataFrame({
    "Produto": ["Arroz 5kg", "Detergente 500ml", "Biscoito 120g", "Azeite 500ml", "Feijão 1kg"],
    "Ruptura_%": [12.3, 8.4, 6.1, 5.4, 4.7]
})
fig_ruptura = px.bar(df_ruptura, x="Produto", y="Ruptura_%", title="Top Rupturas por Produto (Exemplo)")

df_estoque = pd.DataFrame({
    "Produto": ["Refri Lata 269ml", "Shampoo 300ml", "Granola 1kg"],
    "Dias_sem_venda": [75, 68, 92]
})
fig_estoque = px.bar(df_estoque, x="Produto", y="Dias_sem_venda", title="Estoque Parado (>60 dias)")

# --------- Slides (conteúdo) ---------
slides = [
    {
        "title": "Caçulinha BI — Inteligência Conversacional para o Varejo",
        "subtitle": "Apresentação para Diretoria e Gerência",
        "content": [
            "• Assistente conversacional que transforma dados em decisões.",
            "• Integra SQL Server, consultas em linguagem natural e gráficos interativos.",
            "• Foco em reduzir tempo operacional dos OPCOMs e aumentar assertividade."
        ],
        "note": "Use as setas abaixo para navegar pelos slides."
    },
    {
        "title": "Problema",
        "content": [
            "• Tarefas manuais: consultas SQL, consolidação de relatórios, análises repetitivas.",
            "• Decisões reativas por falta de visão consolidada e em tempo hábil.",
            "• Alto custo de contexto para compras e operação."
        ],
        "visual": "emoji:⏱️📑",
    },
    {
        "title": "Solução — Caçulinha BI",
        "content": [
            "• Chat de BI em linguagem natural com dicas de negócio embutidas.",
            "• Dashboards e tabelas em cards modernos (UI com Shadcn/Tailwind).",
            "• Pipeline: Usuário → App (Streamlit) → Agente (LangGraph/LLM) → SQL Server → Gráficos."
        ],
        "visual": "emoji:🤖➡️📊➡️🧠➡️🗄️"
    },
    {
        "title": "Funcionalidades-Chave",
        "content": [
            "• Chat com avatares e input fixo na UI.",
            "• Gráficos (Plotly) e tabelas interativos.",
            "• Dicas de negócio automáticas (rupturas, estoque parado, vendas).",
            "• Suporte a múltiplos usuários e logging estruturado."
        ],
    },
    {
        "title": "Arquitetura Simplificada",
        "content": [
            "• Frontend: Streamlit + (opcional) streamlit-shadcn-ui.",
            "• Inteligência: LangGraph/LLM para orquestração e resposta.",
            "• Dados: SQL Server com consultas parametrizadas.",
            "• Observabilidade: logs, métricas e diagnósticos em aba própria."
        ],
        "visual": "diagram"
    },
    {
        "title": "Benefícios para o Negócio",
        "content": [
            "• Redução do tempo operacional dos OPCOMs.",
            "• Aumento da assertividade nas decisões de compras.",
            "• Insights proativos: priorização de ruptura, queima de estoque parado, curva ABC.",
            "• Escalabilidade para múltiplas lojas e categorias."
        ]
    },
    {
        "title": "Demonstração (Exemplos)",
        "content": [
            "• Vendas por Categoria — visão macro de performance.",
            "• Ruptura por Produto — foco na execução e reposição.",
            "• Estoque Parado — ações de queima/transferência."
        ],
        "plotly": ["vendas", "ruptura", "estoque"]
    },
    {
        "title": "Roadmap",
        "content": [
            "• Curto prazo: UI nova (Shadcn), dicas automáticas, demo robusta.",
            "• Médio prazo: multiusuário, testes automatizados, logging/monitoramento.",
            "• Longo prazo: Docker, CI/CD e expansão de fontes de dados."
        ]
    },
    {
        "title": "Próximos Passos",
        "content": [
            "1) Validar a interface com dados reais (piloto controlado).",
            "2) Priorizar integrações com compras e operação.",
            "3) Habilitar multiusuário e governance de acesso.",
            "4) Planejar rollout por ondas."
        ]
    },
    {
        "title": "Encerramento",
        "subtitle": "O Caçulinha transforma dados em decisões inteligentes.",
        "content": [
            "Obrigado!",
            "Dúvidas e próximos passos."
        ]
    }
]

# --------- Sidebar ---------
with st.sidebar:
    st.markdown("### 📑 Sumário")
    for idx, s in enumerate(slides):
        label = f"{idx+1}. {s['title']}"
        if st.button(label, key=f"goto_{idx}"):
            st.session_state.slide = idx

    st.markdown("---")
    st.caption("Dica: Use ← → (botões abaixo) para avançar/voltar.")

# --------- Navegação ---------
col_prev, col_prog, col_next = st.columns([0.15, 0.7, 0.15])
with col_prev:
    if st.button("⬅️ Voltar"):
        st.session_state.slide = max(0, st.session_state.slide - 1)
with col_prog:
    st.progress((st.session_state.slide + 1) / len(slides))
with col_next:
    if st.button("Avançar ➡️"):
        st.session_state.slide = min(len(slides) - 1, st.session_state.slide + 1)

st.write("")

# --------- Render ---------
slide = slides[st.session_state.slide]

st.title(slide.get("title", ""))
if slide.get("subtitle"):
    st.subheader(slide["subtitle"])

if slide.get("content"):
    for line in slide["content"]:
        st.markdown(f"- {line}")

# Visual extra (diagram or emojis)
if slide.get("visual") == "diagram":
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("**Usuário** 👤")
    with col2:
        st.markdown("➡️")
        st.markdown("**App** (Streamlit)")
    with col3:
        st.markdown("➡️")
        st.markdown("**Agente** (LangGraph/LLM)")
    with col4:
        st.markdown("➡️")
        st.markdown("**BD** (SQL Server)")
    with col5:
        st.markdown("➡️")
        st.markdown("**Insights** 📊")
elif isinstance(slide.get("visual"), str) and slide["visual"].startswith("emoji:"):
    st.markdown(f"### {slide['visual'].split(':', 1)[1]}")

# Plots de demonstração
if "plotly" in slide:
    if "vendas" in slide["plotly"]:
        st.plotly_chart(fig_vendas, use_container_width=True)
    if "ruptura" in slide["plotly"]:
        st.plotly_chart(fig_ruptura, use_container_width=True)
    if "estoque" in slide["plotly"]:
        st.plotly_chart(fig_estoque, use_container_width=True)

# Rodapé
st.markdown("---")
st.caption(f"Caçulinha BI • Apresentação gerada em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
'''

# Save file
path = "/mnt/data/apresentacao_caculinha_bi.py"
with open(path, "w", encoding="utf-8") as f:
    f.write(app_code)

path
