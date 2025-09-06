gemini prompt """
Você é um engenheiro front-end ninja em Streamlit, Tailwind e UX. Preciso que você gere um app.py completo baseado no `streamlit-shadcn-ui` (versão mais recente: 0.1.18), com melhorias visuais e funcionais.

Contexto:
- Framework principal: Streamlit.
- UI: streamlit-shadcn-ui v0.1.18 (pip install streamlit-shadcn-ui).
- Evitar dependências extras, mas usar tailwind via CSS inline se precisar.

Funcionalidades exigidas:
1. Instalar/importar:
   - streamlit-shadcn-ui>=0.1.18
   - streamlit
   - plotly.express para gráficos
   - pandas para dataframes
   - python-dotenv para `.env`
2. Layout do Chat:
   - Chat em balões com avatares (bot vs usuário), usando `ui.avatar` ou CSS custom (Tailwind).
   - Input de texto fixo ao fundo da aba, com botão de enviar com ícone (ex: "📨").
3. Aba Visões:
   - Visualizações salvas em **cards** com bordas arredondadas e sombra (usar `ui.card`).
   - Exibir gráficos Plotly dentro dos cards.
   - DataFrame em tabela (usar `ui.table`) com barra de rolagem e cabeçalho fixo.
   - Tags (badges) para identificar a visão (ex: "Ruptura", "Vendas", "Estoque"), usando `ui.badges`.
4. Aba Diagnóstico:
   - Grid 2 colunas com callouts (ex: SQL conectado, Shadcn ativo, nº de visões geradas), usando `ui.hover_card` ou simples `st.info`.
5. Dark Mode:
   - Toggle `ui.switch` que alterna estilo dark/light (compatível com tema do sistema).
6. Fallback:
   - Se `streamlit-shadcn-ui` não estiver instalado, rodar com visual Streamlit padrão, sem quebrar.
7. Documentação:
   - Ler `.env` (com `python-dotenv`), mostrar DSN SQL e schema no sidebar.
8. Comentários claros no código explicando cada parte.

Resultado esperado:
- Código Python completo (app.py) executável com `streamlit run app.py`.
- Interface moderna, responsiva e funcional.

Saída: O código `app.py` pronto com as bibliotecas e todas as melhorias implementadas.
"""
