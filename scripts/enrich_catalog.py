
import json
import os

def generate_description_from_name(name):
    """
    Gera uma descrição simples a partir do nome da coluna.
    Ex: 'CADASTRO_PRODUTO' -> 'Cadastro Produto'
    """
    return name.replace('_', ' ').capitalize()

def enrich_catalog(input_path, output_path):
    """
    Lê o catálogo de dados, gera descrições iniciais e salva em um novo arquivo.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        for entry in catalog:
            # Gerar descrição para o arquivo
            if entry['description'] == "(Descrição a ser preenchida)":
                file_desc = generate_description_from_name(entry['file_name'].replace('.parquet', ''))
                entry['description'] = f"Dados de {file_desc}."

            # Gerar descrições para as colunas
            for col_name, col_desc in entry['column_descriptions'].items():
                if col_desc == "(Descrição a ser preenchida)":
                    entry['column_descriptions'][col_name] = generate_description_from_name(col_name)
        
        # Salvar o catálogo enriquecido
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=4, ensure_ascii=False)
            
        print(f"Catálogo enriquecido com descrições iniciais salvo em: {output_path}")

    except FileNotFoundError:
        print(f"[!] Erro: O arquivo de catálogo de entrada não foi encontrado em {input_path}")
    except Exception as e:
        print(f"[!] Ocorreu um erro inesperado: {e}")

def main():
    """
    Função principal.
    """
    input_file = "data/data_catalog.json"
    output_file = "data/data_catalog_enriched.json"
    
    print("Iniciando o enriquecimento do catálogo de dados...")
    enrich_catalog(input_file, output_file)

if __name__ == "__main__":
    main()
