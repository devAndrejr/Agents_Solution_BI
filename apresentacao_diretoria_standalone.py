import streamlit as st
import time

# --- Configuração da Página (Adicionado para Standalone) ---
st.set_page_config(
    page_title="Apresentação Agent BI",
    page_icon="🤖",
    layout="wide"
)

# --- CSS Customizado e Injeção de Dependências (Movido para Top-Level) ---
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)
css = """
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
html, body, [class*="st-"] { font-family: 'Roboto', sans-serif; }
.main > div { background-image: linear-gradient(0deg, #f0f2f6, #e6e9f0); }
h1 { font-weight: 700; color: #1E3A8A; letter-spacing: -2px; }
h2, h3 { color: #1E3A8A; font-weight: 400; }
.stButton>button { border-radius: 50px; background-color: #1E3A8A; color: white; border: none; padding: 10px 20px; font-weight: 700; }
.stButton>button:hover { background-color: #2563EB; color: white; }
.card { background-color: white; border-radius: 10px; padding: 25px; margin: 10px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-left: 5px solid #2563EB; }
"""
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# --- Funções de Navegação e Estado ---
if 'slide_number' not in st.session_state:
    st.session_state.slide_number = 0

def next_slide(): st.session_state.slide_number += 1
def prev_slide(): st.session_state.slide_number -= 1

# --- Conteúdo dos Slides ---

def slide_title():
    st.title("🤖 Projeto Agent BI: O Futuro da Análise de Dados")
    st.subheader("Apresentando a evolução de uma ferramenta de BI para uma plataforma de inteligência ativa.")
    st.markdown("---")
    if st.button("Iniciar Apresentação ✨", use_container_width=True):
        st.balloons()
        next_slide()

def slide_agenda():
    st.header("📄 Nossa Jornada")
    st.markdown("""
    - **O Projeto Hoje:** Uma demonstração das capacidades atuais do Agent BI.
    - **A Arquitetura Atual:** Como o sistema funciona por baixo dos panos.
    - **A Visão de Futuro:** A próxima geração do Agent BI.
    - **O Roadmap de Evolução:** Melhorias planejadas na Interface, Inteligência e Engenharia.
    - **Impacto e Próximos Passos.**
    """)

def slide_hoje():
    st.header("📍 O Projeto Hoje: Uma Plataforma de BI Robusta")
    st.markdown("Atualmente, o Agent BI é um sistema completo e funcional que já entrega valor significativo:")
    
    cols = st.columns(2)
    with cols[0]:
        with st.container(border=True):
            st.markdown("##### 📊 Assistente de BI Conversacional")
            st.write("Interface de chat onde usuários fazem perguntas em linguagem natural e recebem respostas, tabelas e gráficos.")
    with cols[1]:
        with st.container(border=True):
            st.markdown("##### 📈 Dashboard Personalizado")
            st.write("Usuários podem fixar os gráficos gerados em um dashboard privado para monitoramento contínuo.")
    cols = st.columns(2)
    with cols[0]:
        with st.container(border=True):
            st.markdown("##### 🧑‍💼 Portal de Gestão de Catálogo")
            st.write("Uma área dedicada para que a equipe de negócio (Compradores) possa refinar as descrições dos dados, melhorando a IA.")
    with cols[1]:
        with st.container(border=True):
            st.markdown("##### ⚙️ Painel de Administração")
            st.write("Controle total sobre usuários, permissões e monitoramento de logs e status dos serviços.")

def slide_arquitetura_atual():
    st.header("🏗️ Arquitetura Atual")
    st.graphviz_chart("""
digraph {
    rankdir="LR";
    graph [bgcolor="transparent"];
    node [shape=box, style="rounded,filled", fillcolor="white", color="#1E3A8A"];
    edge [color="#1E3A8A"];
    
    subgraph cluster_frontend {
        label = "Interface (Streamlit)";
        style="rounded";
        ui [label="App Multi-Página"];
    }
    
    subgraph cluster_backend {
        label = "Backend (FastAPI)";
        style="rounded";
        api [label="API de Consultas e Auth"];
        agent [label="Agente Supervisor (OpenAI)"];
        pipeline [label="Pipeline de Dados Agendado"];
    }
    
    subgraph cluster_data {
        label = "Dados";
        style="rounded";
        db [label="SQL Server & Parquet"];
    }
    
    ui -> api;
    api -> agent;
    agent -> db;
    pipeline -> db;
}
""")

def slide_visao_futuro():
    st.header("🚀 A Visão de Futuro: Uma Plataforma de Inteligência Ativa")
    st.markdown("""
    O próximo salto evolutivo do Agent BI é transcender a análise de dados reativa para se tornar um **parceiro proativo e colaborativo** no processo de tomada de decisão. A evolução se baseia em três pilares fundamentais:
    """)
    cols = st.columns(3)
    cols[0].info("**1. Interface Excepcional:** Uma experiência de usuário moderna, intuitiva e personalizável.")
    cols[1].success("**2. Inteligência Aprimorada:** Um agente de IA mais robusto, contextual e capaz.")
    cols[2].warning("**3. Engenharia de Ponta:** Uma base de código escalável, testável e pronta para o futuro.")

def slide_roadmap_futuro():
    st.header("🗺️ Roadmap de Evolução")
    
    with st.expander("**Pilar 1: Melhorias na Interface (UI/UX)**", expanded=True):
        st.markdown("""- **Adotar Shadcn-UI:** Implementar uma interface moderna com componentes de alta qualidade.\n- **Chat Avançado:** Incluir avatares e uma caixa de input fixa para melhor usabilidade.\n- **Visualizações Modernas:** Usar cards para exibir gráficos e tabelas estilizadas com cabeçalho fixo.\n- **Acessibilidade:** Garantir Dark Mode e feedback visual claro (toasts, loaders).""")

    with st.expander("**Pilar 2: Evolução da Inteligência (IA)**"):
        st.markdown("""- **Implementar LangGraph:** Substituir o agente atual por um supervisor baseado em grafos, permitindo fluxos de decisão mais complexos e robustos.\n- **Respostas Enriquecidas:** Fazer com que a IA não apenas responda, mas também forneça **dicas de negócio automáticas** baseadas nos dados.\n- **Suporte Multi-Usuário Real:** Melhorar a gestão de contexto e histórico de conversas para múltiplos usuários simultâneos.""")

    with st.expander("**Pilar 3: Práticas de Engenharia de Software**"):
        st.markdown("""- **Testes Abrangentes:** Implementar uma suíte de testes unitários e de integração para garantir a confiabilidade.\n- **Logging Estruturado:** Melhorar o monitoramento e a depuração com logs mais detalhados.\n- **Escalabilidade Futura:** Planejar a modularização e o uso de containers (Docker) para facilitar a implantação e o crescimento.\n- **CI/CD:** Adotar práticas de Integração e Entrega Contínua para agilizar o desenvolvimento.""")

def slide_impacto():
    st.header("🎯 Impacto Esperado e Próximos Passos")
    st.markdown("""
    A implementação desta visão transformará o Agent BI de uma ferramenta de consulta em um ativo estratégico indispensável, resultando em:
    
    - **Decisões Mais Rápidas e Inteligentes:** Graças a uma IA proativa e respostas enriquecidas.
    - **Maior Adoção e Satisfação do Usuário:** Devido a uma interface de altíssima qualidade.
    - **Redução de Riscos e Custos de Manutenção:** Com uma base de código robusta e testada.
    
    **Nossos próximos passos imediatos são focar no Pilar 1, iniciando a integração da nova interface com Shadcn-UI.**
    """)

def slide_qa():
    st.balloons()
    st.title("Obrigado!")
    st.header("Perguntas e Respostas")

# --- Lógica Principal de Execução e Navegação ---

def render_navigation(slides):
    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns([2,1,2,1,2])
    with col2:
        if st.session_state.slide_number > 0:
            st.button("⬅️ Anterior", on_click=prev_slide, use_container_width=True)
    with col4:
        if st.session_state.slide_number < len(slides) - 1:
            st.button("Próximo ➡️", on_click=next_slide, use_container_width=True)

slides = [
    slide_title,
    slide_agenda,
    slide_hoje,
    slide_arquitetura_atual,
    slide_visao_futuro,
    slide_roadmap_futuro,
    slide_impacto,
    slide_qa
]

current_slide_func = slides[st.session_state.slide_number]
current_slide_func()

render_navigation(slides)
