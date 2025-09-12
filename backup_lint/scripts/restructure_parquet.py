# scripts/restructure_parquet.py

import pandas as pd
import os

# Define os diretórios de origem e destino
SOURCE_DIR = "data/parquet"
DEST_DIR = "data/parquet_cleaned"

# Garante que o diretório de destino exista
os.makedirs(DEST_DIR, exist_ok=True)

# Carrega o arquivo "padrão ouro" para obter a estrutura de colunas
print("Carregando o esquema de ADMMATAO.parquet...")
try:
    target_schema_df = pd.read_parquet(os.path.join(SOURCE_DIR, "ADMMATAO.parquet"))
    target_columns = target_schema_df.columns.tolist()
    print(f"Esquema de destino carregado com {len(target_columns)} colunas.")
except Exception as e:
    print(f"Erro ao carregar o esquema de ADMMATAO.parquet: {e}")
    exit()

# --- Mapeamento de Colunas --- #
# Este dicionário mapeia os nomes de colunas antigos (dos arquivos de origem) para os novos nomes (do arquivo de destino)

map_admat = {
    'CDIGO': 'PRODUTO',
    'NOME': 'NOME',
    'FABRICANTE': 'NomeFabricante',
    'EMBALAGEM': 'EMBALAGEM',
    'PREO 38%': 'LIQUIDO_38',
    'MST C/': 'QTDE_EMB_MASTER',
    'MUL C/': 'QTDE_EMB_MULTIPLO',
    'EM LINHA': 'FORALINHA', # Pode precisar de transformação (boolean invert?)
    'SEGMENTO': 'NOMESEGMENTO',
    'CATEGORIA': 'NomeCategoria',
    'GRUPO': 'NOMEGRUPO',
    'SUBGRUPO': 'NomeSUBGRUPO',
    'EM PROMO': 'PROMOCIONAL',
    'VENDA 30D': 'VENDA_30DD',
    'EAN': 'EAN',
    'EST. CD': 'ESTOQUE_CD',
    'ULT. ENT. CD': 'ULTIMA_ENTRADA_DATA_CD',
    'EST. UNE': 'ESTOQUE_UNE',
    'ULT. ENT. UNE': 'ULTIMA_ENTRADA_DATA_UNE',
    'EST. LV': 'ESTOQUE_LV',
    'EST.GON': 'ESTOQUE_GONDOLA_LV',
    'EST. ILHA': 'ESTOQUE_ILHA_LV',
    'EXPO. MIN': 'EXPOSICAO_MINIMA',
    'TRAVA': 'MEDIA_TRAVADA',
    'END. GNDO': 'ENDERECO_LINHA',
    'PP': 'PONTO_PEDIDO_LV',
    'LT': 'LEADTIME_LV',
    'END. ESTOQUE': 'ENDERECO_RESERVA',
    'SOLICITAO': 'SOLICITACAO_PENDENTE',
    'QTD SOL': 'SOLICITACAO_PENDENTE_QTDE',
    'DATA SOL': 'SOLICITACAO_PENDENTE_DATA',
    'STATUS': 'SOLICITACAO_PENDENTE_SITUACAO',
    'ULTIMA_VENDA': 'ULTIMA_VENDA_DATA_UNE',
    'PICKLIST': 'PICKLIST',
    'ST PICK': 'PICKLIST_SITUACAO',
    'DATA CONFERNCIA': 'PICKLIST_CONFERENCIA',
    'ULT VOL': 'ULTIMO_VOLUME',
    'QTD VOL': 'VOLUME_QTDE',
    'ROMANEIO SOLICITA': 'ROMANEIO_SOLICITACAO',
    'ROMANEIO ENVIO': 'ROMANEIO_ENVIO',
    'NOTA ENVIO': 'NOTA',
    'S': 'SERIE',
    'EMISSAO NOTA': 'NOTA_EMISSAO',
    'FREQ ULT. SEM': 'FREQ_ULT_SEM',
}

map_admat_semvendas = {
    'CDIGO': 'PRODUTO',
    'NOME': 'NOME',
    'FABRICA': 'NomeFabricante',
    'EMBALAGEM': 'EMBALAGEM',
    'PREO 38%': 'LIQUIDO_38',
    'MST C/': 'QTDE_EMB_MASTER',
    'MUL C/': 'QTDE_EMB_MULTIPLO',
    'EM LINHA': 'FORALINHA',
    'SEGMENTO': 'NOMESEGMENTO',
    'CATEGORIA': 'NomeCategoria',
    'GRUPO': 'NOMEGRUPO',
    'SUBGRUPO': 'NomeSUBGRUPO',
    'EST. UNE': 'ESTOQUE_UNE',
    'EXPO. MIN': 'EXPOSICAO_MINIMA',
    'TRAVA': 'MEDIA_TRAVADA',
    'END. ESTOQUE UNE': 'ENDERECO_RESERVA',
}

def restructure_parquet(source_filename, dest_filename, column_mapping):
    source_path = os.path.join(SOURCE_DIR, source_filename)
    dest_path = os.path.join(DEST_DIR, dest_filename)

    print(f"\nProcessando {source_filename}...")

    try:
        # Carrega o arquivo de origem
        source_df = pd.read_parquet(source_path)
        print(f"Lido {source_filename} com {len(source_df.columns)} colunas e {len(source_df)} linhas.")

        # Cria um novo DataFrame com o esquema de destino, preenchido com Nulos
        restructured_df = pd.DataFrame(columns=target_columns)

        # Renomeia as colunas do DataFrame de origem de acordo com o mapeamento
        source_df.rename(columns=column_mapping, inplace=True)

        # Preenche o novo DataFrame com os dados do antigo
        for col in restructured_df.columns:
            if col in source_df.columns:
                restructured_df[col] = source_df[col]

        # Lógica de transformação especial
        if 'FORALINHA' in restructured_df.columns:
            # Exemplo: se a coluna original era 'EM LINHA' (booleano), podemos precisar inverter.
            # Esta é uma suposição e pode precisar de ajuste.
            # Se 'EM LINHA' for 'S' ou 'N', a lógica seria diferente.
            # Assumindo que 'EM LINHA' é 1 para sim e 0 para não, e 'FORALINHA' é o inverso.
            if 'FORALINHA' in source_df.columns: # Verifica se a coluna existia antes do mapeamento
                 pass # Nenhuma transformação por enquanto, apenas copiando

        print(f"Colunas reestruturadas. O novo DataFrame tem {len(restructured_df.columns)} colunas.")

        # Salva o novo arquivo Parquet
        restructured_df.to_parquet(dest_path, index=False)
        print(f"Arquivo salvo com sucesso em: {dest_path}")

    except Exception as e:
        print(f"Ocorreu um erro ao processar {source_filename}: {e}")

if __name__ == "__main__":
    restructure_parquet("ADMAT.parquet", "ADMAT_structured.parquet", map_admat)
    restructure_parquet("ADMAT_SEMVENDAS.parquet", "ADMAT_SEMVENDAS_structured.parquet", map_admat_semvendas)
