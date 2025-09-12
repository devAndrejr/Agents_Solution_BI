import pandas as pd
import os

def inspect_segment_categories(file_path, segment_column, segment_value, category_column):
    """
    Carrega um arquivo Parquet e inspeciona as categorias de um segmento específico.
    """
    try:
        df = pd.read_parquet(file_path)
        
        if segment_column in df.columns and category_column in df.columns:
            # Filtra o segmento, ignorando o caso
            segment_df = df[df[segment_column].str.lower() == segment_value.lower()]
            
            if not segment_df.empty:
                unique_categories = segment_df[category_column].unique()
                print(f"Categorias únicas para o segmento '{segment_value}':")
                for category in unique_categories:
                    print(category)
            else:
                print(f"Nenhum dado encontrado para o segmento '{segment_value}'.")
        else:
            print(f"Uma das colunas '{segment_column}' ou '{category_column}' não foi encontrada.")
            
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    parquet_file = os.path.join(os.getcwd(), "data", "parquet_cleaned", "ADMAT_REBUILT.parquet")
    segment_col = "nomesegmento"
    segment_val = "TECIDOS"
    category_col = "nome_categoria"
    
    print(f"Inspecionando as categorias do segmento '{segment_val}'...")
    inspect_segment_categories(parquet_file, segment_col, segment_val, category_col)
    print("Inspeção concluída.")
