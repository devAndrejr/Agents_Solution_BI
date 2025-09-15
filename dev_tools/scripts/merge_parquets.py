# scripts/merge_parquets.py

import pandas as pd
import os

# Define os diretórios
SOURCE_DIR_ORIGINAL = "data/parquet"
SOURCE_DIR_CLEANED = "data/parquet_cleaned"
DEST_DIR = "data/parquet_cleaned"

# Nomes dos arquivos
file_admmatao = os.path.join(SOURCE_DIR_ORIGINAL, "ADMMATAO.parquet")
file_admat = os.path.join(SOURCE_DIR_CLEANED, "ADMAT_structured.parquet")
file_admat_semvendas = os.path.join(SOURCE_DIR_CLEANED, "ADMAT_SEMVENDAS_structured.parquet")

# Nome do arquivo de saída
output_file = os.path.join(DEST_DIR, "master_catalog.parquet")

print("Iniciando a fusão dos arquivos Parquet...")

# --- Funções de Padronização ---
def standardize_boolean_column(series):
    series_str = series.astype(str).str.upper().str.strip()
    mapping = {
        'S': True, 'SIM': True, 'TRUE': True, '1': True,
        'N': False, 'NAO': False, 'FALSE': False, '0': False, '-': False
    }
    return series_str.map(mapping).astype("boolean")

def standardize_integer_column(series):
    numeric_series = pd.to_numeric(series, errors='coerce')
    rounded_series = numeric_series.round(0)
    return rounded_series.astype('Int64')

def standardize_date_column(series):
    return pd.to_datetime(series, errors='coerce')

# --- Listas de Colunas por Tipo ---
boolean_cols = ['PROMOCIONAL', 'FORALINHA', 'MEDIA_TRAVADA']
integer_cols = [
    'QTDE_EMB_MASTER', 'QTDE_EMB_MULTIPLO', 'ESTOQUE_CD', 'ULTIMA_ENTRADA_QTDE_CD',
    'ESTOQUE_UNE', 'ULTIMA_ENTRADA_QTDE_UNE', 'ESTOQUE_LV', 'ESTOQUE_GONDOLA_LV',
    'ESTOQUE_ILHA_LV', 'EXPOSICAO_MINIMA', 'EXPOSICAO_MINIMA_UNE', 'EXPOSICAO_MAXIMA_UNE',
    'LEADTIME_LV', 'PONTO_PEDIDO_LV', 'SOLICITACAO_PENDENTE_QTDE', 'VOLUME_QTDE',
    'PICKLIST', 'ULTIMO_VOLUME', 'ROMANEIO_SOLICITACAO', 'NOTA', 'SERIE',
    'VENDA_30DD', 'FREQ_ULT_SEM'
]
date_cols = [
    'ULTIMA_ENTRADA_DATA_CD', 'ULTIMA_ENTRADA_DATA_UNE', 'ULTIMO_INVENTARIO_UNE',
    'SOLICITACAO_PENDENTE_DATA', 'ULTIMA_VENDA_DATA_UNE', 'PICKLIST_CONFERENCIA',
    'NOTA_EMISSAO', 'ROMANEIO_ENVIO'
]

try:
    # Carrega os três arquivos
    print("Carregando arquivos...")
    df_admmatao = pd.read_parquet(file_admmatao)
    df_admat = pd.read_parquet(file_admat)
    df_admat_semvendas = pd.read_parquet(file_admat_semvendas)

    # --- Limpeza de Dados ---
    print("Padronizando os tipos de dados das colunas...")
    for df in [df_admmatao, df_admat, df_admat_semvendas]:
        for col in boolean_cols:
            if col in df.columns:
                df[col] = standardize_boolean_column(df[col])
        
        for col in integer_cols:
            if col in df.columns:
                df[col] = standardize_integer_column(df[col])

        for col in date_cols:
            if col in df.columns:
                df[col] = standardize_date_column(df[col])

    print(f"Linhas em ADMMATAO: {len(df_admmatao)}")
    print(f"Linhas em ADMAT_structured: {len(df_admat)}")
    print(f"Linhas em ADMAT_SEMVENDAS_structured: {len(df_admat_semvendas)}")

    # Concatena os DataFrames
    print("Concatenando os DataFrames...")
    master_df = pd.concat([df_admmatao, df_admat, df_admat_semvendas], ignore_index=True)

    print(f"Total de linhas no arquivo mestre: {len(master_df)}")

    # Salva o DataFrame mestre
    print(f"Salvando o arquivo mestre em {output_file}...")
    master_df.to_parquet(output_file, index=False)

    print("\nFusão concluída com sucesso!")
    print(f"Arquivo mestre salvo em: {output_file}")

except Exception as e:
    print(f"\nOcorreu um erro durante a fusão: {e}")