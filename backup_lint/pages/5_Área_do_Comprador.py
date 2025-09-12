import streamlit as st
import pandas as pd
import json
import os

# --- Verificação de Autenticação ---
if st.session_state.get("authentication_status"):
    # --- Configuração da Página ---
    st.set_page_config(
        page_title="Área do Comprador - Gestão de Catálogo",
        page_icon="🧑‍💼",
        layout="wide"
    )

    st.title("🧑‍💼 Gestão do Catálogo de Dados")
    st.markdown("""
    Use esta página para refinar as descrições dos dados. 
    O seu conhecimento de negócio é essencial para que o agente de IA possa entender as perguntas dos usuários e encontrar as respostas corretas.
    """)

    # O resto do código da página continua aqui...
else:
    st.error("Acesso negado. Por favor, faça o login na página principal para acessar esta área.")
    st.stop()

# --- Constantes ---
CATALOG_FILE_PATH = "data/CATALOGO_PARA_EDICAO.json"

# --- Funções Auxiliares ---
def load_catalog():
    """Carrega o catálogo de dados do arquivo JSON."""
    if not os.path.exists(CATALOG_FILE_PATH):
        st.error(f"Erro: Arquivo de catálogo não encontrado em `{CATALOG_FILE_PATH}`. Execute os scripts de geração primeiro.")
        return None
    with open(CATALOG_FILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_catalog(catalog_data):
    """Salva os dados do catálogo de volta no arquivo JSON."""
    with open(CATALOG_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog_data, f, indent=4, ensure_ascii=False)
    st.success("Catálogo salvo com sucesso!")

# --- Lógica da Interface ---
catalog = load_catalog()

if catalog:
    # Seleção do arquivo de dados para editar
    file_names = [entry['file_name'] for entry in catalog]
    selected_file = st.selectbox("**1. Selecione o conjunto de dados que deseja editar:**", file_names)

    if selected_file:
        # Encontrar a entrada do catálogo para o arquivo selecionado
        selected_entry = next((item for item in catalog if item["file_name"] == selected_file), None)
        
        st.markdown("---_**2. Refine as descrições abaixo:**_---")

        # Editar a descrição geral do arquivo
        st.markdown("#### Descrição Geral do Conjunto de Dados")
        st.caption("Explique o que este conjunto de dados representa. Ex: Cadastro de produtos, vendas diárias, etc.")
        selected_entry['description'] = st.text_area(
            "Descrição do Arquivo:", 
            value=selected_entry.get('description', ''),
            label_visibility="collapsed"
        )

        # Editar as descrições das colunas em uma tabela
        st.markdown("#### Descrições das Colunas")
        st.caption("Para cada coluna, explique o que ela significa. O agente usará isso para encontrar a informação certa.")
        
        col_descriptions = selected_entry.get('column_descriptions', {})
        col_names = list(col_descriptions.keys())
        
        # Criar um DataFrame para edição com st.data_editor
        editor_df = pd.DataFrame({
            'Coluna': col_names,
            'Descrição': [col_descriptions.get(col, '') for col in col_names]
        })
        
        edited_df = st.data_editor(
            editor_df,
            column_config={
                "Coluna": st.column_config.TextColumn("Nome da Coluna", disabled=True),
                "Descrição": st.column_config.TextColumn("Descrição (Editável)", width="large", help="Clique para editar a descrição.")
            },
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic"
        )

        # Botão para salvar as alterações
        st.markdown("---_**3. Salve suas alterações**_---")
        if st.button("Salvar Alterações no Catálogo", type="primary"):
            # Atualizar o dicionário do catálogo com os dados editados
            new_descriptions = dict(zip(edited_df['Coluna'], edited_df['Descrição']))
            selected_entry['column_descriptions'] = new_descriptions
            
            # Salvar o catálogo completo de volta no arquivo
            save_catalog(catalog)