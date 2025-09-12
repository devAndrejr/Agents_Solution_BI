import json
import os
import re

def to_snake_case(name):
    """
    Converte um nome de coluna para snake_case.
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return s2.replace(' ', '_')

def merge_catalogs():
    """
    Mescla o catálogo de dados gerado com o catálogo focado.
    """
    data_catalog_path = os.path.join(os.getcwd(), "data", "data_catalog.json")
    focused_catalog_path = os.path.join(os.getcwd(), "data", "catalog_focused.json")
    
    try:
        with open(data_catalog_path, 'r', encoding='utf-8') as f:
            data_catalog = json.load(f)
            
        with open(focused_catalog_path, 'r', encoding='utf-8') as f:
            focused_catalog = json.load(f)

        # Encontra a entrada para ADMAT_REBUILT.parquet nos dois catálogos
        admat_rebuilt_new = next((item for item in data_catalog if item["file_name"] == "ADMAT_REBUILT.parquet"), None)
        admat_rebuilt_old = next((item for item in focused_catalog if item["file_name"] == "ADMAT_REBUILT.parquet"), None)

        if admat_rebuilt_new and admat_rebuilt_old:
            # Pega as descrições do catálogo antigo
            description = admat_rebuilt_old.get("description", "(Descrição a ser preenchida)")
            old_column_descriptions = admat_rebuilt_old.get("column_descriptions", {})
            
            # Mapeia as descrições para os novos nomes de coluna
            new_column_descriptions = {to_snake_case(old_col): desc for old_col, desc in old_column_descriptions.items()}
            
            # Atualiza a nova entrada do catálogo
            admat_rebuilt_new["description"] = description
            admat_rebuilt_new["column_descriptions"] = new_column_descriptions
            
            # Cria o novo catálogo focado
            new_focused_catalog = [admat_rebuilt_new]
            
            # Salva o novo catálogo focado
            with open(focused_catalog_path, 'w', encoding='utf-8') as f:
                json.dump(new_focused_catalog, f, indent=4, ensure_ascii=False)
                
            print("Catálogo focado atualizado com sucesso.")
            
        else:
            print("Não foi possível encontrar a entrada para 'ADMAT_REBUILT.parquet' em um dos catálogos.")

    except Exception as e:
        print(f"Erro ao mesclar os catálogos: {e}")

if __name__ == "__main__":
    merge_catalogs()
