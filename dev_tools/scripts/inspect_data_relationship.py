
import pandas as pd
import os

# Path to the parquet file
parquet_file_path = os.path.join('data', 'parquet_cleaned', 'admatao.parquet')

print(f"Analyzing relationships in {parquet_file_path}...")

try:
    # Load the dataframe
    df = pd.read_parquet(parquet_file_path)

    # --- Analysis 1: What categories exist within the 'tecidos' segment? ---
    print("\n--- Analysis 1: Categories within the 'tecidos' segment ---")
    
    # Ensure column is lowercase for consistent filtering
    df['NOMESEGMENTO_lower'] = df['NOMESEGMENTO'].str.lower()
    
    df_tecidos = df[df['NOMESEGMENTO_lower'] == 'tecidos']

    if df_tecidos.empty:
        print("No data found for the 'tecidos' segment.")
    else:
        unique_categories_in_tecidos = df_tecidos['NomeCategoria'].unique().tolist()
        print("Unique categories found within the 'tecidos' segment:")
        print(unique_categories_in_tecidos)

    # --- Analysis 2: Show all combinations of segment and category ---
    print("\n--- Analysis 2: All Segment/Category Combinations ---")
    segment_category_combinations = df[['NOMESEGMENTO', 'NomeCategoria']].drop_duplicates().sort_values(by=['NOMESEGMENTO', 'NomeCategoria'])
    
    print("Found the following combinations of Segment and Category in the data:")
    # Use to_string() to ensure all rows are printed
    print(segment_category_combinations.to_string())

except Exception as e:
    print(f"An error occurred: {e}")
