import pandas as pd
import glob
import os
import json

def generate_catalog_for_file(file_path):
    """
    Gera uma entrada de catálogo para um único arquivo Parquet.
    """
    print(f"- Gerando metadados para: {os.path.basename(file_path)}")
    try:
        df = pd.read_parquet(file_path)
        
        schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        catalog_entry = {
            "file_name": os.path.basename(file_path),
            "row_count": len(df),
            "column_count": len(df.columns),
            "schema": schema,
            "description": "(Descrição a ser preenchida)", # Placeholder para descrição manual
            "column_descriptions": {col: "(Descrição a ser preenchida)" for col in df.columns} # Placeholders
        }
        return catalog_entry

    except Exception as e:
        print(f"  [!] Erro ao processar {os.path.basename(file_path)}: {e}")
        return None

def main():
    """
    Função principal para gerar o catálogo de dados.
    """
    input_dir = "data/parquet_cleaned/"
    output_file = "data/data_catalog.json"
    
    parquet_files = glob.glob(os.path.join(input_dir, "*.parquet"))
    
    if not parquet_files:
        print(f"Nenhum arquivo Parquet limpo encontrado em '{input_dir}'.")
        return
        
    print(f"Encontrados {len(parquet_files)} arquivos. Gerando catálogo de metadados...")
    
    data_catalog = []
    for file in parquet_files:
        entry = generate_catalog_for_file(file)
        if entry:
            data_catalog.append(entry)
            
    # Salvar o catálogo em um arquivo JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data_catalog, f, indent=4, ensure_ascii=False)
        
    print(f"\nCatálogo de dados salvo com sucesso em: {output_file}")

if __name__ == "__main__":
    main()
