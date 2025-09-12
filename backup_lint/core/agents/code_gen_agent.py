# core/agents/code_gen_agent.py
import logging
import os
import json
import re
import pandas as pd
import time
import plotly.express as px
from typing import List, Dict, Any # Import necessary types
import threading
from queue import Queue
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import io
import sys
import plotly.io as pio
import uuid

from core.llm_base import BaseLLMAdapter

class CodeGenAgent:
    """
    Agente especializado em gerar e executar código Python para análise de dados.
    """
    def __init__(self, llm_adapter: BaseLLMAdapter):
        """
        Inicializa o agente, carregando o LLM, o catálogo de dados e o diretório de dados.
        """
        self.logger = logging.getLogger(__name__)
        self.llm = llm_adapter # Use o adaptador injetado
        self.parquet_dir = os.path.join(os.getcwd(), "data", "parquet_cleaned")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self._load_vector_store()
        self.code_cache = {}
        self.logger.info("CodeGenAgent inicializado com RAG e cache de código.")

    def _load_vector_store(self):
        """Carrega o vector store do arquivo."""
        vector_store_path = os.path.join(os.getcwd(), "data", "vector_store.pkl")
        try:
            with open(vector_store_path, 'rb') as f:
                vector_store_data = pickle.load(f)
                self.index = faiss.deserialize_index(vector_store_data['index'])
                self.metadata = vector_store_data['metadata']
            self.logger.info("Vector store carregado com sucesso.")
        except FileNotFoundError:
            self.logger.error(f"Arquivo vector_store.pkl não encontrado em {vector_store_path}. O RAG não funcionará.")
            self.index = None
            self.metadata = []

    def _get_catalog_timestamp(self) -> float:
        """Retorna o timestamp da última modificação do arquivo de catálogo."""
        catalog_path = os.path.join(os.getcwd(), "data", "catalog_focused.json")
        try:
            return os.path.getmtime(catalog_path)
        except FileNotFoundError:
            self.logger.warning(f"Arquivo de catálogo não encontrado em {catalog_path}. Retornando timestamp 0.")
            return 0.0

    def _find_relevant_columns(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Encontra as colunas mais relevantes para a query usando o FAISS."""
        if not self.index:
            return []
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding, dtype=np.float32), k)
        
        relevant_columns = []
        for i in indices[0]:
            relevant_columns.append(self.metadata[i])
        return relevant_columns

    def _build_rag_prompt(self, query: str, relevant_columns: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Constrói o prompt para o LLM com base nas colunas relevantes."""
        system_message = {
            "role": "system",
            "content": """
            Você é um assistente de BI especializado em gerar código Python para análise de dados.
            Siga as instruções cruciais de análise de dados para gerar um script Python completo e executável.
            Você deve usar o arquivo 'admatao.parquet' para todas as consultas de dados.
            A coluna que representa o ID do produto neste arquivo é 'PRODUTO'.
            """
        }

        # Constrói o contexto com as colunas relevantes
        context = "\n".join([f"- Tabela: {col['table_name']}, Coluna: {col['column_name']}, Descrição: {col['column_description']}" for col in relevant_columns])

        user_message = {
            "role": "user",
            "content": f"""
            **Instruções Cruciais de Análise de Dados:**
            1.  **Use o Contexto Fornecido:** Baseie-se exclusivamente no contexto de colunas fornecido abaixo para decidir quais arquivos Parquet carregar e quais colunas usar. Não invente colunas ou arquivos.
            2.  **Caminho dos Arquivos:** Os arquivos Parquet estão localizados no diretório `{self.parquet_dir}`. Use esta variável para construir o caminho para os arquivos.
            3.  **Aplique Filtros:** Se a pergunta do usuário contiver condições (ex: "no segmento tecidos", "para o produto X"), traduza-as em filtros do Pandas (`df[df['coluna'] == 'valor']`).
            4.  **Use a biblioteca Pandas** para manipulação de dados.
            **IMPORTANTE:** Sempre trate os tipos de dados das colunas antes de usá-las. Para colunas que podem conter números (como vendas mensais 'MES_XX'), converta-as para numérico, tratando erros e preenchendo NaNs. Para colunas de texto (como IDs ou categorias), converta para string e minúsculas para comparação.
                **ATENÇÃO:** As colunas de vendas mensais no arquivo `admatao.parquet` estão em MAIÚSCULAS (ex: 'MES_01', 'MES_02', etc.). Certifique-se de usar a capitalização correta ao referenciá-las.
                Exemplos de conversão de tipo:
                - Para colunas numéricas (ex: 'MES_XX'): `df['MES_XX'] = pd.to_numeric(df['MES_XX'], errors='coerce').fillna(0)`
                - Para colunas de texto (ex: 'PRODUTO', 'NomeCategoria'): `df['COLUNA_TEXTO'] = df['COLUNA_TEXTO'].astype(str).str.lower()`
            5.  **Contexto de Colunas Relevantes:**
                ```
                {context}
                ```
            6.  **Carregue os DataFrames necessários** a partir dos arquivos Parquet. A variável `parquet_dir` já está disponível no ambiente de execução. Use-a para construir o caminho. Ex: `df = pd.read_parquet(os.path.join(parquet_dir, "NOME_DO_ARQUIVO.parquet"))`
            7.  **Analise os dados** para responder à pergunta do usuário.
            8.  **Armazene o resultado final** (seja um texto, um número, um DataFrame ou uma figura Plotly) em uma variável chamada `result`.
            9.  **Ordenação para Gráficos:** Para gráficos de linha ou de barras onde a ordem do eixo X é importante (como tempo ou categorias sequenciais), **SEMPRE ORDENE** o DataFrame pela coluna do eixo X antes de criar o gráfico. Ex: `df_grafico = df_grafico.sort_values(by='coluna_do_eixo_x')`.
            10. Se a pergunta exigir um gráfico, use a biblioteca Plotly Express.
            11. **O seu código deve ser um script Python completo e executável.** Não inclua explicações ou texto adicional fora do código.
            12. **Verifique a Disponibilidade dos Dados:** Se o contexto não fornecer colunas para responder à pergunta, armazene na variável `result` uma mensagem informativa como: 'Não consigo responder a essa pergunta com os dados disponíveis.'
            13. **NÃO chame .show() ou print()** no seu código. Apenas armazene o objeto final (DataFrame, figura Plotly, ou texto) na variável `result`.
            14. **Tratamento de Dados Vazios:** Se, após a filtragem ou processamento, o DataFrame resultante estiver vazio ou não contiver dados suficientes para a análise/gráfico solicitado, armazene na variável `result` uma mensagem clara e amigável informando o usuário que não há dados disponíveis para a consulta específica (ex: 'Não foram encontrados dados de vendas para o produto X no período Y.').

            **Pergunta do Usuário:** "{query}"

            **Exemplo de Uso:**

            **Pergunta do Usuário:** "Qual o total de vendas por categoria nos últimos 3 meses?"

            **Script Python Ideal:**
            ```python
            import pandas as pd
            import plotly.express as px
            import os
            from datetime import datetime, timedelta

            # Carregar dados de vendas e produtos
            df_vendas = pd.read_parquet(os.path.join(parquet_dir, "vendas.parquet"))
            df_produtos = pd.read_parquet(os.path.join(parquet_dir, "produtos.parquet"))

            # Converter coluna de data para datetime
            df_vendas['data_venda'] = pd.to_datetime(df_vendas['data_venda'])

            # Calcular a data de 3 meses atrás
            data_limite = datetime.now() - timedelta(days=90)

            # Filtrar vendas dos últimos 3 meses
            df_vendas_recentes = df_vendas[df_vendas['data_venda'] >= data_limite]

            # Unir com dados de produtos para obter a categoria
            df_merged = pd.merge(df_vendas_recentes, df_produtos[['produto_id', 'categoria']], on='produto_id', how='left')

            # Calcular total de vendas por categoria
            vendas_por_categoria = df_merged.groupby('categoria')['valor_venda'].sum().reset_index()
            vendas_por_categoria.columns = ['Categoria', 'Total de Vendas']

            # Armazenar o resultado
            result = vendas_por_categoria
            ```

            **Pergunta do Usuário:** "Mostre as vendas mensais do produto X em um gráfico de linha."

            **Script Python Ideal:**
            ```python
            import pandas as pd
            import plotly.express as px
            import os

            # Carregar dados do produto
            df_produto = pd.read_parquet(os.path.join(parquet_dir, "admatao.parquet"))

            # Filtrar pelo produto específico (substitua 'X' pelo ID do produto real)
            produto_id = "369947" # Exemplo, o LLM deve extrair isso da pergunta
            df_produto_filtrado = df_produto[df_produto['PRODUTO'] == produto_id]

            # Colunas de vendas mensais (ex: 'MES_01', 'MES_02', etc.)
            colunas_meses = [f'MES_{{i:02d}}' for i in range(1, 13)]
            colunas_vendas_presentes = [col for col in colunas_meses if col in df_produto_filtrado.columns]

            # Se não houver colunas de vendas, retorne uma mensagem
            if not colunas_vendas_presentes:
                result = f"Não foram encontradas colunas de vendas mensais para o produto {{produto_id}}."
            else:
                # Transformar dados de formato largo para longo (unpivot)
                df_long = df_produto_filtrado.melt(
                    id_vars=['PRODUTO'],
                    value_vars=colunas_vendas_presentes,
                    var_name='Mês',
                    value_name='Vendas'
                )

                # Converter a coluna de vendas para numérico, tratando erros
                df_long['Vendas'] = pd.to_numeric(df_long['Vendas'], errors='coerce').fillna(0)

                # Agrupar por Mês e somar as Vendas para evitar a distorção
                df_vendas_mensais = df_long.groupby('Mês')['Vendas'].sum().reset_index()

                # Ordenar os dados pelo mês para garantir a ordem cronológica
                df_vendas_mensais = df_vendas_mensais.sort_values(by='Mês')

                # Criar o gráfico de barras, conforme a imagem
                fig = px.bar(
                    df_vendas_mensais,
                    x='Mês',
                    y='Vendas',
                    title=f'Vendas Mensais do Produto {{produto_id}}',
                    labels={{'Mês': 'Mês', 'Vendas': 'Vendas'}}
                )
                
                # Armazenar o resultado
                result = fig
            ```

            **Pergunta do Usuário:** "Mostre um gráfico de dispersão das vendas vs. lucro."

            **Script Python Ideal:**
            ```python
            import pandas as pd
            import plotly.express as px
            import os

            # Carregar dados (assumindo que 'admatao.parquet' contém vendas e lucro)
            df_dados = pd.read_parquet(os.path.join(parquet_dir, "admatao.parquet"))

            # Certificar-se de que as colunas são numéricas
            df_dados['VENDAS'] = pd.to_numeric(df_dados['VENDAS'], errors='coerce').fillna(0)
            df_dados['LUCRO'] = pd.to_numeric(df_dados['LUCRO'], errors='coerce').fillna(0)

            # Criar o gráfico de dispersão
            fig = px.scatter(df_dados, x='VENDAS', y='LUCRO', title='Vendas vs. Lucro')

            # Armazenar o resultado
            result = fig
            ```

            **Pergunta do Usuário:** "Mostre um histograma da distribuição de preços."

            **Script Python Ideal:**
            ```python
            import pandas as pd
            import plotly.express as px
            import os

            # Carregar dados (assumindo que 'admatao.parquet' contém a coluna de preço)
            df_dados = pd.read_parquet(os.path.join(parquet_dir, "admatao.parquet"))

            # Certificar-se de que a coluna de preço é numérica
            df_dados['PREÇO'] = pd.to_numeric(df_dados['PREÇO'], errors='coerce').fillna(0)

            # Criar o histograma
            fig = px.histogram(df_dados, x='PREÇO', title='Distribuição de Preços')

            # Armazenar o resultado
            result = fig
            ```

            **Script Python:**
            ```python
            import pandas as pd
            import plotly.express as px
            import os

            # Escreva seu código aqui
            result = None # Inicialize a variável de resultado
            ```
            """
        }
        return [system_message, user_message]

    def _execute_generated_code(self, code: str, local_scope: Dict[str, Any]):
        q = Queue()
        output_capture = io.StringIO()
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        def worker():
            sys.stdout = output_capture
            sys.stderr = output_capture
            try:
                exec(code, local_scope)
                q.put(local_scope.get('result'))
            except Exception as e:
                q.put(e)
            finally:
                sys.stdout = original_stdout
                sys.stderr = original_stderr

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=120.0)

        captured_output = output_capture.getvalue()
        if captured_output:
            self.logger.info(f"Saída do código gerado:\n{captured_output}")

        if thread.is_alive():
            raise TimeoutError("A execução do código gerado excedeu o tempo limite.")
        else:
            result = q.get()
            if isinstance(result, Exception):
                raise result
            return result

    def generate_and_execute_code(self, query: str) -> dict:
        """
        Gera, executa e retorna o resultado do código Python para uma dada consulta.
        """
        self.logger.info(f'Iniciando geração e execução de código para a consulta: "{query}"')
        
        current_catalog_timestamp = self._get_catalog_timestamp()
        cache_key = (query, current_catalog_timestamp)

        # Tenta buscar o código no cache
        if cache_key in self.code_cache:
            code_to_execute = self.code_cache[cache_key]
            self.logger.info(f"Código recuperado do cache para a consulta: \"{query}\"")
        else:
            # Encontra colunas relevantes usando RAG
            relevant_columns = self._find_relevant_columns(query)
            
            messages = self._build_rag_prompt(query, relevant_columns)

            start_llm_query = time.time()
            llm_response = self.llm.get_completion(messages=messages) # Use get_completion with messages
            end_llm_query = time.time()
            self.logger.info(f"Tempo de consulta LLM: {end_llm_query - start_llm_query:.4f} segundos")

            if "error" in llm_response:
                self.logger.error(f"Erro ao obter resposta do LLM: {llm_response['error']}")
                return {"type": "error", "output": "Não foi possível gerar o código de análise. Por favor, tente reformular sua pergunta ou contate o suporte."}

            code_to_execute = self._extract_python_code(llm_response.get("content", "")) # Extract content

            if not code_to_execute:
                self.logger.warning("Nenhum código Python foi gerado pelo LLM.")
                return {"type": "text", "output": "Não consegui gerar um script para responder à sua pergunta. Tente reformulá-la."}
            
            # Armazena o código gerado no cache
            self.code_cache[cache_key] = code_to_execute

        self.logger.info(f"""
Código gerado pelo LLM (ou recuperado do cache):
{code_to_execute}
""" )

        try:
            local_scope = {
                "parquet_dir": self.parquet_dir,
                "pd": pd,
                "px": px,
                "os": os,
                "result": None
            }
            
            # Definir o tema padrão do Plotly para garantir consistência visual
            px.defaults.template = "plotly_white"

            start_code_execution = time.time()
            result = self._execute_generated_code(code_to_execute, local_scope)
            end_code_execution = time.time()
            self.logger.info(f"Tempo de execução do código: {end_code_execution - start_code_execution:.4f} segundos")

            if isinstance(result, pd.DataFrame):
                self.logger.info(f"Resultado do código gerado (DataFrame): {result.head()}")
                return {"type": "dataframe", "output": result}
            elif 'plotly' in str(type(result)):
                self.logger.info(f"Resultado do código gerado (Chart): {type(result)}")
                # Serializar o objeto Plotly Figure para JSON
                chart_json = pio.to_json(result)
                return {"type": "chart", "output": chart_json}
            else:
                self.logger.info(f"Resultado do código gerado (Texto): {result}")
                return {"type": "text", "output": str(result)}
        
        except TimeoutError:
            self.logger.error("A execução do código gerado excedeu o tempo limite.")
            return {"type": "error", "output": "A análise dos dados demorou muito para ser concluída e foi interrompida. Tente uma pergunta mais simples."}
        except Exception as e:
            self.logger.error(f"Erro ao executar o código gerado: {e}", exc_info=True)
            return {"type": "error", "output": "Ocorreu um erro ao executar a análise de dados. Por favor, verifique sua pergunta ou contate o suporte."}

    def _extract_python_code(self, text: str) -> str | None:
        """Extrai o bloco de código Python da resposta do LLM."""
        match = re.search(r'```python\n(.*)```', text, re.DOTALL)
        return match.group(1).strip() if match else None