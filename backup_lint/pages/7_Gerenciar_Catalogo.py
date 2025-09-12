import streamlit as st
import json
import os
import pandas as pd
import pandas as pd
from core.session_state import SESSION_STATE_KEYS

CATALOG_PATH = "data/catalog_focused.json"

def load_catalog():
    if not os.path.exists(CATALOG_PATH):
        return []
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_catalog(catalog):
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=4, ensure_ascii=False)

def show_catalog_manager():
    st.markdown("<h1>⚙️ Gerenciar Catálogo de Dados</h1>", unsafe_allow_html=True)

    # Admin check
    if st.session_state.get(SESSION_STATE_KEYS["ROLE"]) != "admin":
        st.warning("Você não tem permissão para acessar esta página.")
        st.stop()

    catalog = load_catalog()

    st.subheader("Fontes de Dados Atuais")
    if catalog:
        # Display catalog in a more readable format
        df_catalog = pd.DataFrame(catalog)
        st.dataframe(df_catalog[['file_name', 'description', 'row_count', 'column_count']], use_container_width=True)
    else:
        st.info("Nenhuma fonte de dados no catálogo ainda.")

    st.subheader("Adicionar Nova Fonte de Dados")
    with st.form("add_data_source_form"):
        new_file_name = st.text_input("Nome do Arquivo (ex: vendas.parquet)")
        new_description = st.text_area("Descrição da Fonte de Dados")
        
        # For simplicity, schema and column_descriptions will be added as empty for now
        # A more advanced UI would allow adding columns dynamically
        
        submitted = st.form_submit_button("Adicionar Fonte de Dados")
        if submitted:
            if new_file_name:
                new_entry = {
                    "file_name": new_file_name,
                    "row_count": 0, # Placeholder
                    "column_count": 0, # Placeholder
                    "schema": {},
                    "description": new_description,
                    "column_descriptions": {}
                }
                catalog.append(new_entry)
                save_catalog(catalog)
                st.success(f"Fonte de dados '{new_file_name}' adicionada com sucesso!")
                st.rerun()
            else:
                st.error("O nome do arquivo não pode ser vazio.")

    st.subheader("Editar Fonte de Dados Existente")
    if catalog:
        selected_file_name = st.selectbox("Selecione a Fonte de Dados para Editar", [d['file_name'] for d in catalog])
        selected_index = next((i for i, d in enumerate(catalog) if d['file_name'] == selected_file_name), None)

        if selected_index is not None:
            selected_entry = catalog[selected_index]
            with st.form("edit_data_source_form"):
                edited_description = st.text_area("Descrição", value=selected_entry['description'])
                
                st.markdown("#### Editar Colunas")
                # Display existing columns and allow editing descriptions
                edited_columns = {}
                for col_name, col_desc in selected_entry['column_descriptions'].items():
                    edited_columns[col_name] = st.text_input(f"Descrição da Coluna: {col_name}", value=col_desc, key=f"edit_col_{selected_file_name}_{col_name}")
                
                # Allow adding new columns (simple text input for name and description)
                new_col_name = st.text_input("Nome da Nova Coluna")
                new_col_desc = st.text_input("Descrição da Nova Coluna")

                edit_submitted = st.form_submit_button("Salvar Alterações")
                if edit_submitted:
                    selected_entry['description'] = edited_description
                    selected_entry['column_descriptions'] = edited_columns
                    if new_col_name and new_col_desc:
                        selected_entry['schema'][new_col_name] = "object" # Default type
                        selected_entry['column_descriptions'][new_col_name] = new_col_desc
                        selected_entry['column_count'] = len(selected_entry['schema']) # Update count
                    
                    save_catalog(catalog)
                    st.success(f"Fonte de dados '{selected_file_name}' atualizada com sucesso!")
                    st.rerun()
    else:
        st.info("Adicione uma fonte de dados primeiro para poder editá-la.")

# Call the function to display the page
show_catalog_manager()