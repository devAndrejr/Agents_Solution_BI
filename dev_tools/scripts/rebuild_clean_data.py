
import pandas as pd
import os

def rebuild_and_clean_data(source_path, admat_path, destination_path):
    """Lê o arquivo Parquet bruto, o limpa, adiciona a coluna COMPRADOR e o salva como uma nova fonte de verdade."""
    print(f"--- Reconstruindo a partir de: {os.path.basename(source_path)} ---")
    try:
        df = pd.read_parquet(source_path)
        
        # Carregar ADMAT.parquet para obter a coluna COMPRADOR
        print(f"--- Carregando dados do comprador de: {os.path.basename(admat_path)} ---")
        df_admat = pd.read_parquet(admat_path)
        comprador_df = df_admat[['CODIGO', 'COMPRADOR']].copy()
        comprador_df.drop_duplicates(subset=['CODIGO'], inplace=True)

        # Mapeamento de renomeação de colunas (de bruto para limpo)
        column_rename_map = {
            'PRODUTO': 'CODIGO',
            'NOME': 'NOME_PRODUTO',
            'LIQUIDO_38': 'PRECO_38PERCENT',
            'VENDA_30DD': 'VENDA_30D',
            'ESTOQUE_UNE': 'ESTOQUE_ATUAL'
            # Adicione outros mapeamentos conforme necessário para padronização
        }
        df.rename(columns=column_rename_map, inplace=True)
        print(f"{len(column_rename_map)} colunas foram renomeadas para o novo padrão.")

        # Identifica colunas que devem ser numéricas
        cols_to_convert = [col for col in df.columns if 'MES_' in col or 'QTDE_' in col or 'MEDIA_' in col or 'VENDA_' in col or 'PRECO_' in col or 'ESTOQUE_' in col]
        
        print(f"Convertendo {len(cols_to_convert)} colunas para tipo numérico...")
        for col in cols_to_convert:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Merge da coluna COMPRADOR
        print("--- Adicionando coluna COMPRADOR ---")
        df = pd.merge(df, comprador_df, on='CODIGO', how='left')
        print(f"Coluna COMPRADOR adicionada. Total de valores não nulos: {df['COMPRADOR'].notna().sum()}")

        # Salva o novo DataFrame limpo e reconstruído
        df.to_parquet(destination_path, index=False)
        print(f"\nArquivo reconstruído e limpo salvo com sucesso em: {destination_path}")
        print(f"Dimensões finais -> Linhas: {len(df)}, Colunas: {len(df.columns)}")

    except Exception as e:
        print(f"Ocorreu um erro durante a reconstrução: {e}")

if __name__ == "__main__":
    source_file = os.path.join(os.getcwd(), "data", "parquet", "ADMMATAO.parquet")
    admat_file = os.path.join(os.getcwd(), "data", "parquet_cleaned", "ADMAT.parquet")
    destination_file = os.path.join(os.getcwd(), "data", "parquet_cleaned", "ADMAT_REBUILT.parquet")

    if os.path.exists(source_file) and os.path.exists(admat_file):
        rebuild_and_clean_data(source_file, admat_file, destination_file)
    else:
        if not os.path.exists(source_file):
            print(f"ERRO: Arquivo fonte não encontrado: {source_file}")
        if not os.path.exists(admat_file):
            print(f"ERRO: Arquivo de compradores não encontrado: {admat_file}")
