from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine

# Configurações
caminho_arquivo_excel = r"S:\Meu Drive\Caçula\Job\ADMAT_BON_9.3_070524_01h57.xlsm"
planilhas = ["ADMAT_SEMVENDAS"]
linha_inicial = 11

# Credenciais do banco
MSSQL_SERVER = "FAMILIA\\SQLJR"
MSSQL_DATABASE = "Projeto_Caculinha"
MSSQL_USER = "AgenteVirtual"
MSSQL_PASSWORD = "Cacula@2020"
DB_DRIVER = "ODBC Driver 17 for SQL Server"
TRUST_SERVER_CERTIFICATE = "yes"
ENCRYPT = "no"

# String ODBC igual ao seu teste que funcionou
odbc_str = (
    f"DRIVER={{{DB_DRIVER}}};"
    f"SERVER={MSSQL_SERVER};"
    f"DATABASE={MSSQL_DATABASE};"
    f"UID={MSSQL_USER};"
    f"PWD={MSSQL_PASSWORD};"
    f"TrustServerCertificate={TRUST_SERVER_CERTIFICATE};"
    f"Encrypt={ENCRYPT};"
)
connection_uri = f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc_str)}"


# Função para ler planilha
def ler_planilha(nome):
    df = pd.read_excel(
        caminho_arquivo_excel,
        sheet_name=nome,
        header=linha_inicial - 1,
        engine="openpyxl",
    )
    # Garante que todos os nomes de coluna são string
    df.columns = df.columns.map(str)
    # Remove colunas totalmente vazias
    df = df.dropna(axis=1, how="all")
    # Remove colunas "Unnamed" (opcional, se não quiser nenhuma coluna sem nome)
    # Se quiser manter todas, comente a linha abaixo:
    # df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    print(f"\nPlanilha: {nome}")
    print("Colunas e tipos detectados:")
    print(df.dtypes)
    print(f"Total de colunas após limpeza: {len(df.columns)}")
    return df


# Ler dados
dfs = {}
for planilha in planilhas:
    try:
        dfs[planilha] = ler_planilha(planilha)
    except Exception as e:
        print(f"Erro ao ler {planilha}: {e}")
        dfs[planilha] = None

# Conectar ao banco
engine = create_engine(connection_uri)

# Criar tabelas e inserir dados
for nome, df in dfs.items():
    if df is not None and not df.empty:
        print(f"\nCriando e populando tabela {nome}...")
        df.to_sql(name=nome, con=engine, if_exists="replace", index=False)
        print(f"Tabela {nome} criada e populada com {len(df)} linhas.")
    else:
        print(f"Dados não encontrados para {nome}.")

print("\nProcesso concluído.")
