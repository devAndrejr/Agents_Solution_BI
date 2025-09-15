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
from core.utils.json_utils import _clean_json_values # Import the cleaning function

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
        self.parquet_dir = os.path.join(os.getcwd(), "data", "parquet")
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
        catalog_path = os.path.join(os.getcwd(), "data", "catalog_cleaned.json")
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
                        Você deve usar o arquivo 'admatao.parquet' para todas as consultas de dados.
                        CRÍTICO: Use EXATAMENTE os nomes de colunas fornecidos, respeitando maiúsculas/minúsculas.
            """
        }

        # Constrói o contexto com as colunas relevantes
        context = "\n".join([f"- Tabela: {col['table_name']}, Coluna: {col['column_name']}, Descrição: {col['column_description']}" for col in relevant_columns])

        # Adiciona lista de colunas mais importantes com nomes corretos
        main_columns = """
COLUNAS PRINCIPAIS DISPONÍVEIS (use exatamente como mostrado):
- nomesegmento (texto - segmento do produto)
- nome_categoria (texto - categoria do produto)
- nomegrupo (texto - grupo do produto)
- nome_produto (texto - nome do produto)
- nome_fabricante (texto - fabricante)
- mes_01, mes_02, mes_03, mes_04, mes_05, mes_06, mes_07, mes_08, mes_09, mes_10, mes_11, mes_12 (numérico - vendas mensais)
- mes_parcial (numérico - vendas do mês parcial atual)
- estoque_atual (numérico - estoque atual)
- estoque_cd (numérico - estoque CD)
- preco_38_percent (numérico - preço)
- une_nome (texto - nome da unidade)
- codigo (numérico - código do produto)

IMPORTANTE PARA ANÁLISES TEMPORAIS:
- Para gráficos de evolução/tendência: Use TODAS as colunas mes_01 até mes_12
- Para "últimos X meses": Use mes_12, mes_11, mes_10, etc. (do mais recente para o mais antigo)
- Para "primeiros X meses": Use mes_01, mes_02, mes_03, etc.
- Para criar gráficos temporais: transforme os dados em formato longo (melt) com mês e valor
        """

        user_message = {
            "role": "user",
            "content": f"""
            **Instruções Cruciais de Análise de Dados:**
            1.  **Use o Contexto Fornecido:** Baseie-se exclusivamente no contexto de colunas fornecido abaixo para decidir quais colunas usar. Não invente colunas.
            2.  **Use a biblioteca Pandas** para manipulação de dados.
            **IMPORTANTE:** Sempre trate os tipos de dados das colunas antes de usá-las. Para colunas que podem conter números (como vendas mensais), converta-as para numérico, tratando erros e preenchendo NaNs. Para colunas de texto, converta para string.
                **ATENÇÃO CRÍTICA:** Use EXATAMENTE os nomes de colunas conforme estão no DataFrame. Principais colunas disponíveis:
                - Segmento: 'nomesegmento' (minúsculas)
                - Categoria: 'nome_categoria' (com underline)
                - Grupo: 'nomegrupo' (minúsculas)
                - Produto: 'nome_produto' (com underline)
                - Vendas mensais: 'mes_01', 'mes_02', ..., 'mes_12' (minúsculas com underline)
                - Estoque: 'estoque_atual', 'estoque_cd', 'estoque_lv'
                - Fabricante: 'nome_fabricante' (com underline)
                - Código: 'codigo' (sem acento)

                **EXEMPLOS DE USO CORRETO:**
                - Para colunas numéricas: `df['mes_01'] = pd.to_numeric(df['mes_01'], errors='coerce').fillna(0)`
                - Para colunas de texto: `df['nomesegmento'] = df['nomesegmento'].astype(str)`

                **PARA ANÁLISES TEMPORAIS:**
                - Evolução de vendas: `vendas_cols = ['mes_01', 'mes_02', 'mes_03', 'mes_04', 'mes_05', 'mes_06', 'mes_07', 'mes_08', 'mes_09', 'mes_10', 'mes_11', 'mes_12']`
                - Transformar para formato longo: `df_melted = pd.melt(df, id_vars=['codigo', 'nome_produto'], value_vars=vendas_cols, var_name='mes', value_name='vendas')`
                - Gráfico temporal: `fig = px.line(df_melted, x='mes', y='vendas', title='Evolução de Vendas')`
            3.  **Contexto de Colunas Relevantes:**
                ```
                {context}
                ```

            {main_columns}
            4.  **A variável `df_raw_data` já contém um Pandas DataFrame com os dados brutos.** Use-a como sua fonte de dados principal. Você NÃO precisa carregar arquivos Parquet novamente.
            5.  **Analise os dados** para responder à pergunta do usuário.
            6.  **Armazene o resultado final** em uma variável chamada `result`.
            7.  **Para Geração de Gráficos:**
                *   Se a pergunta exigir um gráfico, use a biblioteca `plotly.express`.
                *   A variável `result` **DEVE** conter um objeto `plotly.graph_objects.Figure`.
                *   **Selecione as colunas apropriadas** de `df_raw_data` para os eixos X e Y, baseando-se na pergunta do usuário e nos tipos de dados das colunas.
                *   **Escolha o tipo de gráfico mais adequado** (ex: `px.bar` para categorias, `px.line` para séries temporais, `px.scatter` para correlações).
                *   **PARA GRÁFICOS TEMPORAIS/EVOLUÇÃO:**
                    - Se o usuário pedir "evolução", "tendência", "ao longo do tempo", "mensais", "últimos meses":
                    - Use pd.melt() para transformar mes_01-mes_12 em formato longo
                    - Exemplo: `df_melted = pd.melt(df_filtered, id_vars=['codigo', 'nome_produto'], value_vars=['mes_01', 'mes_02', 'mes_03', 'mes_04', 'mes_05', 'mes_06', 'mes_07', 'mes_08', 'mes_09', 'mes_10', 'mes_11', 'mes_12'], var_name='mes', value_name='vendas')`
                    - Use px.line() para mostrar tendência temporal
                    - Para "últimos X meses": filtre apenas as colunas relevantes antes do melt
                *   **SEMPRE ORDENE** o DataFrame pela coluna do eixo X antes de criar o gráfico, se a ordem for importante (como tempo ou categorias sequenciais). Ex: `df_grafico = df_grafico.sort_values(by='coluna_do_eixo_x')`.
                *   Adicione um título significativo ao gráfico.
            8.  **O seu código deve ser um script Python completo e executável.** Não inclua explicações ou texto adicional fora do código.
            9.  **Verifique a Disponibilidade dos Dados:** Se o `df_raw_data` estiver vazio ou não contiver dados suficientes para a análise/gráfico solicitado, armazene na variável `result` uma mensagem clara e amigável informando o usuário que não há dados disponíveis para a consulta específica (ex: 'Não foram encontrados dados para a sua consulta.').
            10. **NÃO chame .show() ou print()** no seu código. Apenas armazene o objeto final (DataFrame, figura Plotly, ou texto) na variável `result`.

            **Exemplo de Script Python para Gráfico de Barras:**
            ```python
            import pandas as pd
            import plotly.express as px

            # df_raw_data já está disponível e contém os dados
            # Exemplo de processamento (se necessário)
            # df_processado = df_raw_data.groupby('CATEGORIA')['VENDAS'].sum().reset_index()

            # Crie seu gráfico Plotly Express aqui
            fig = px.bar(df_raw_data, x="NomeCategoria", y="MES_01", title="Vendas por Categoria no Mês 01")
            result = fig
            ```

            **Script Python:**
            ```python
            import pandas as pd
            import plotly.express as px

            # df_raw_data já está disponível aqui como um Pandas DataFrame
            # Escreva seu código aqui
            result = None # Armazene o resultado final aqui (DataFrame, figura Plotly, ou texto)
            ```
            """
        }
        return [system_message, user_message]

    def _fix_column_names(self, code: str, df_columns: list) -> str:
        """Corrige automaticamente nomes de colunas incorretos no código gerado."""
        # Mapeamento de nomes incorretos comuns para corretos
        column_fixes = {
            'NOMESEGMENTO': 'nomesegmento',
            'NOME_CATEGORIA': 'nome_categoria',
            'NOMEGRUPO': 'nomegrupo',
            'NOME_PRODUTO': 'nome_produto',
            'NOME_FABRICANTE': 'nome_fabricante',
            'ESTOQUE_UNE': 'estoque_atual',
            'ESTOQUE_CD': 'estoque_cd',
            'NOME': 'nome_produto',
            'UNE_NOME': 'une_nome',
            'PRODUTO': 'nome_produto',
            'FABRICANTE': 'nome_fabricante'
        }

        # Adiciona correções para colunas de mês
        for i in range(1, 13):
            column_fixes[f'MES_{i:02d}'] = f'mes_{i:02d}'

        # Aplica as correções
        fixed_code = code
        for wrong_name, correct_name in column_fixes.items():
            if correct_name in df_columns:  # Só corrige se a coluna existe
                fixed_code = fixed_code.replace(f"'{wrong_name}'", f"'{correct_name}'")
                fixed_code = fixed_code.replace(f'"{wrong_name}"', f'"{correct_name}"')

        return fixed_code

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

    def generate_and_execute_code(self, input_data: Dict[str, Any]) -> dict:
        """
        Gera, executa e retorna o resultado do código Python para uma dada consulta.
        """
        query = input_data.get("query", "")
        raw_data = input_data.get("raw_data", [])
        
        current_catalog_timestamp = self._get_catalog_timestamp()
        # Use a hash of the query and a hash of the raw_data (converted to a string) for the cache key
        # This ensures the cache key is hashable and reflects changes in raw_data
        raw_data_cleaned = _clean_json_values(raw_data)
        raw_data_hash = hash(json.dumps(raw_data_cleaned, sort_keys=True)) if raw_data_cleaned else 0
        cache_key = (query, current_catalog_timestamp, raw_data_hash)

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

        # Criar o DataFrame para verificar as colunas
        df_raw_data = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()

        # Corrigir nomes de colunas incorretos automaticamente
        if not df_raw_data.empty:
            code_to_execute = self._fix_column_names(code_to_execute, df_raw_data.columns.tolist())

        self.logger.info(f"""
Código gerado pelo LLM (após correções):
{code_to_execute}
""" )

        try:
            local_scope = {
                "parquet_dir": self.parquet_dir,
                "pd": pd,
                "px": px,
                "os": os,
                "result": None,
                "df_raw_data": df_raw_data
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
