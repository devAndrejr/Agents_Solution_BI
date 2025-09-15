# Este script serve como um blueprint para a orquestração futura dos pipelines de dados.
# Ele define a sequência lógica de execução dos scripts, mas não os executa diretamente.
# Em uma implementação real com ferramentas como Airflow ou Mage, cada "passo" aqui
# seria uma tarefa (task) dentro de um DAG (Directed Acyclic Graph).

import subprocess
import os

def run_script(script_path):
    """Executa um script Python e retorna seu status."""
    print(f"Executando: {script_path}")
    # Usar python.exe para garantir que o ambiente virtual seja respeitado
    # Assumindo que o script está na pasta 'scripts/' e o executável python está no PATH
    # ou pode ser referenciado diretamente.
    # Para um ambiente de orquestração real, o caminho do interpretador Python
    # e o diretório de trabalho seriam configurados pela ferramenta.
    try:
        # Ajuste o caminho para o executável python se necessário
        # Por exemplo, se estiver em um venv: os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.venv', 'Scripts', 'python.exe')
        # Para simplicidade, assumimos que 'python' está no PATH ou que o orquestrador gerencia isso.
        result = subprocess.run(['python', script_path], check=True, capture_output=True, text=True)
        print(f"Saída de {script_path}:\n{result.stdout}")
        if result.stderr:
            print(f"Erros de {script_path}:\n{result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar {script_path}: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"Erro: O interpretador 'python' ou o script '{script_path}' não foi encontrado.")
        return False

def main_pipeline():
    """Define a sequência de execução do pipeline de dados do Caçulinha BI."""
    print("Iniciando pipeline de dados do Caçulinha BI...")

    # Caminho base para os scripts, relativo ao diretório raiz do projeto
    # Em um orquestrador, esses caminhos seriam absolutos ou gerenciados pelo ambiente.
    scripts_base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts')

    # Passo 1: Exportar dados do SQL Server para Parquet
    export_script = os.path.join(scripts_base_path, 'export_sqlserver_to_parquet.py')
    if not run_script(export_script):
        print("Falha na exportação do SQL Server para Parquet. Abortando pipeline.")
        return

    # Passo 2: Limpar dados Parquet
    clean_script = os.path.join(scripts_base_path, 'clean_parquet_data.py')
    if not run_script(clean_script):
        print("Falha na limpeza dos dados Parquet. Abortando pipeline.")
        return

    # Passo 3: Unir arquivos Parquet
    merge_script = os.path.join(scripts_base_path, 'merge_parquets.py')
    if not run_script(merge_script):
        print("Falha na união dos arquivos Parquet. Abortando pipeline.")
        return

    print("Pipeline de dados do Caçulinha BI concluído com sucesso!")

if __name__ == "__main__":
    main_pipeline()
