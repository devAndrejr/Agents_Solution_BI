import pandas as pd
from sqlalchemy import create_engine, types
import urllib
import traceback
import subprocess # Para executar comandos do sistema (bcp)
import os # Para lidar com caminhos de arquivo

# ==============================================================================
# SEÇÃO 1: CONFIGURAÇÕES
# ==============================================================================
SERVER = 'FAMILIA\SQLJR'
DATABASE = 'Projeto_Caculinha'
USERNAME = 'AgenteVirtual'
PASSWORD = 'Cacula@2020'
TABLE_NAME = 'ADMMATAO'
SCHEMA_NAME = 'dbo'
FILE_PATH = 'data/parquet/ADMMATAO.parquet'
TEMP_CSV_PATH = 'temp_upload_data.csv' # Arquivo CSV temporário que será criado

# ==============================================================================
# SEÇÃO 2: FUNÇÃO DE LIMPEZA DE DADOS (Inalterada)
# ==============================================================================
def treat_data(df: pd.DataFrame) -> pd.DataFrame:
    print("Iniciando processo de limpeza e tratamento dos dados...")
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip().replace({'': None, 'nan': None, '<NA>': None, 'None': None})
        elif pd.api.types.is_numeric_dtype(df[col]):
            df[col] = pd.to_numeric(df[col], errors='coerce')
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col], errors='coerce')
    print("Limpeza e tratamento de dados concluídos.")
    return df

# ==============================================================================
# SEÇÃO 3: LÓGICA PRINCIPAL COM BCP
# ==============================================================================
if __name__ == "__main__":
    try:
        # --- ETAPA 1: EXTRAÇÃO E TRANSFORMAÇÃO ---
        print(f"Lendo o arquivo Parquet de: {FILE_PATH}")
        df = pd.read_parquet(FILE_PATH)
        df_cleaned = treat_data(df)
        print(f"Total de {len(df_cleaned)} linhas limpas para importar.")

        # --- ETAPA 2: PREPARAÇÃO DO BANCO DE DADOS ---
        # Conectamos ao banco para criar a estrutura da tabela vazia. O bcp não cria tabelas.
        quoted_password = urllib.parse.quote_plus(PASSWORD)
        connection_string = f'mssql+pyodbc://{USERNAME}:{quoted_password}@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(connection_string)
        
        print("\nConectando ao SQL Server para criar a estrutura da tabela...")
        # Mapeamento completo para garantir a criação correta da tabela
        dtype_mapping = {
            'CODIGO_EMPRESA': types.BigInteger(), 'CODIGO_PRODUTO': types.BigInteger(), 'CODIGO_GRUPO': types.BigInteger(),
            'EMPRESA': types.VARCHAR(None), 'PRODUTO_INI': types.VARCHAR(None), 'PRODUTO_FIN': types.VARCHAR(None), 'GRUPO': types.VARCHAR(None),
            'SUBGRUPO': types.VARCHAR(None), 'CATEGORIA': types.VARCHAR(None), 'MARCA': types.VARCHAR(None), 'FORNECEDOR': types.VARCHAR(None),
            'COD_BARRAS_INI': types.VARCHAR(None), 'COD_BARRAS_FIN': types.VARCHAR(None), 'ESTOQUE_MINIMO': types.BigInteger(),
            'ESTOQUE_MAXIMO': types.BigInteger(), 'QTD_ESTOQUE': types.Numeric(18, 6), 'CUSTO_ULTIMO': types.Numeric(18, 6),
            'CUSTO_REPOSICAO': types.Numeric(18, 6), 'CUSTO_MEDIO': types.Numeric(18, 6), 'PRECO_VENDA': types.Numeric(18, 6),
            'PRECO_VENDA_ANTERIOR': types.Numeric(18, 6), 'PRECO_OFERTA': types.Numeric(18, 6), 'PRECO_OFERTA_ANTERIOR': types.Numeric(18, 6),
            'ESTOQUE_CRITICO': types.VARCHAR(None), 'OBSERVACAO': types.VARCHAR(None), 'SITUACAO_PRODUTO': types.VARCHAR(None),
            'SITUACAO_CADASTRO': types.VARCHAR(None), 'DATA_CADASTRO': types.DateTime(), 'DATA_ULTIMA_COMPRA': types.DateTime(),
            'DATA_ULTIMA_VENDA': types.DateTime(), 'EMBALAGEM_COMPRA': types.BigInteger(), 'EMBALAGEM_VENDA': types.BigInteger(),
            'ALIQUOTA_ICMS': types.Numeric(18, 6), 'ALIQUOTA_IPI': types.Numeric(18, 6), 'ALIQUITA_PIS': types.Numeric(18, 6),
            'ALIQUOTA_COFINS': types.Numeric(18, 6), 'ALIQUOTA_FRETE': types.Numeric(18, 6), 'COMISSAO': types.Numeric(18, 6),
            'DESCONTO_MAXIMO': types.Numeric(18, 6), 'PESO_BRUTO': types.Numeric(18, 6), 'PESO_LIQUIDO': types.Numeric(18, 6),
            'DATA_OFERTA_INI': types.DateTime(), 'DATA_OFERTA_FIN': types.DateTime(), 'PROMOCAO_INI': types.VARCHAR(None),
            'PROMOCAO_FIN': types.VARCHAR(None), 'PROMOCAO_TIPO': types.VARCHAR(None), 'PROMOCAO_APLICACAO': types.VARCHAR(None),
            'PROMOCAO_FIDELIDADE': types.VARCHAR(None), 'PROMOCAO_PRECO': types.Numeric(18, 6), 'PROMOCAO_DESCONTO': types.Numeric(18, 6),
            'PROMOCAO_LEVE': types.BigInteger(), 'PROMOCAO_PAGUE': types.BigInteger(), 'PRECO_ATACADO': types.Numeric(18, 6),
            'QTD_ATACADO': types.Numeric(18, 6), 'PRECO_PRAZO': types.Numeric(18, 6), 'QTD_PRAZO': types.Numeric(18, 6),
            'NCM': types.VARCHAR(None), 'ATIVO_COMPRA': types.VARCHAR(None), 'ATIVO_VENDA': types.VARCHAR(None),
            'CODIGO_SUBGRUPO': types.BigInteger(), 'CODIGO_CATEGORIA': types.BigInteger(), 'CODIGO_MARCA': types.BigInteger(),
            'CODIGO_FORNECEDOR': types.BigInteger(), 'ESTOQUE_LOJA': types.Numeric(18, 6), 'ESTOQUE_DEPOSITO': types.Numeric(18, 6),
            'ESTOQUE_TOTAL': types.Numeric(18, 6), 'ESTOQUE_RESERVADO': types.Numeric(18, 6), 'ESTOQUE_DISPONIVEL': types.Numeric(18, 6),
            'ESTOQUE_PEDIDO': types.Numeric(18, 6), 'UNE': types.VARCHAR(None), 'UNIDADE': types.BigInteger(),
            'ORIGEM_PRODUTO': types.BigInteger(), 'UN': types.VARCHAR(None), 'FATOR': types.VARCHAR(None), 'TEM_ESTOQUE': types.VARCHAR(None),
            'GIRO': types.VARCHAR(None), 'CST': types.VARCHAR(None), 'DATA_ULTIMA_ATUALIZACAO': types.DateTime(),
            'PRECO_CREDITO': types.Numeric(18, 16), 'MARGEM_LUCRO': types.Numeric(18, 16), 'DIAS_ESTOQUE': types.Numeric(18, 16),
            'ULTIMO_FORNECEDOR': types.VARCHAR(None), 'ULTIMA_ATUALIZACAO': types.DateTime(), 'PRECO_DEBITO': types.Numeric(18, 16),
            'PRECO_PIX': types.Numeric(18, 16), 'MARGEM': types.Numeric(18, 16), 'LUCRO': types.Numeric(18, 16),
            'ULTIMA_COMPRA': types.VARCHAR(None), 'ULTIMA_VENDA': types.VARCHAR(None), 'ID_PRODUTO': types.Float(53),
            'ID_EMPRESA': types.Float(53), 'QTD_COMPRADA': types.BigInteger(), 'ID_FILIAL': types.VARCHAR(None),
            'ID_GRUPO': types.VARCHAR(None), 'ID_SUBGRUPO': types.VARCHAR(None), 'ID_CATEGORIA': types.VARCHAR(None),
            'DATA_HORA_CADASTRO': types.DateTime(), 'MARGEM_DESEJADA': types.VARCHAR(None), 'CUSTO_NF': types.VARCHAR(None),
            'PRECO_NF': types.VARCHAR(None), 'PRECO_VENDA_PROMOCAO': types.VARCHAR(None), 'DATA_INICIAL_PROMOCAO': types.VARCHAR(None),
            'DATA_FINAL_PROMOCAO': types.VARCHAR(None), 'PRECO_VENDA_ATACADO': types.VARCHAR(None),
            'QTD_MINIMA_ATACADO': types.VARCHAR(None), 'ATIVO': types.Float(53)
        }
        # Enviamos apenas o cabeçalho (0 linhas) para criar a tabela com a estrutura correta
        df_cleaned.head(0).to_sql(name=TABLE_NAME, con=engine, schema=SCHEMA_NAME, if_exists='replace', index=False, dtype=dtype_mapping)
        print(f"Tabela '{TABLE_NAME}' criada/substituída com sucesso no banco.")

        # --- ETAPA 3: CARGA NATIVA COM BCP ---
        print(f"\nSalvando dados limpos em arquivo CSV temporário: {TEMP_CSV_PATH}")
        # Salva em CSV com encoding UTF-8, sem cabeçalho e com um separador pipe '|' que é mais seguro que vírgula
        df_cleaned.to_csv(TEMP_CSV_PATH, index=False, header=False, sep='|', encoding='utf-8-sig')

        print("Iniciando upload em massa com BCP...")
        # Monta o comando BCP
        bcp_command = [
            'bcp',
            f'{DATABASE}.{SCHEMA_NAME}.{TABLE_NAME}',
            'in',
            TEMP_CSV_PATH,
            '-S', SERVER,
            '-U', USERNAME,
            '-P', PASSWORD,
            '-c',          # Indica dados de caractere
            '-t', '|',     # Especifica o separador pipe
            '-C', '65001'  # Especifica a Code Page para UTF-8
        ]
        
        # Executa o comando BCP
        result = subprocess.run(bcp_command, capture_output=True, text=True, encoding='latin1')

        # Verifica o resultado
        if result.returncode == 0:
            print("\n" + "="*70)
            print(">>> UPLOAD COM BCP CONCLUÍDO COM SUCESSO! <<<")
            print(result.stdout) # Mostra a saída do BCP
            print("="*70)
        else:
            print("\n" + "="*70)
            print("!!! ERRO DURANTE A EXECUÇÃO DO BCP !!!")
            print("="*70)
            print("\nSaída do BCP (stdout):")
            print(result.stdout)
            print("\nErro do BCP (stderr):")
            print(result.stderr)
    
    except Exception:
        print("\nOcorreu um erro crítico no script Python. Detalhes completos abaixo:")
        print(traceback.format_exc())
    
    finally:
        # Limpa o arquivo CSV temporário
        if os.path.exists(TEMP_CSV_PATH):
            os.remove(TEMP_CSV_PATH)
            print(f"\nArquivo temporário '{TEMP_CSV_PATH}' removido.")