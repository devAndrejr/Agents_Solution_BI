import logging
import re
import sys # Adicionado para depuração
import ast # Adicionado para converter string para dicionário
from datetime import datetime, timedelta
import pandas as pd # Importar pandas

from core.utils.db_utils import get_table_df


import json
from core.agents.caculinha_bi_agent import initialize_agent_for_session

class ProductAgent:
    """
    Agente para consulta e análise de produtos, usando apenas Parquet.
    """

    PRODUCT_TABLES = ["ADMAT", "Admat_OPCOM"]

    def __init__(self):
        self.logger = logging.getLogger("ProductAgent")
        self.catalog = self._load_catalog()
        # Inicializa o agente LLM que será usado para raciocinar sobre os dados
        self.llm_agent = initialize_agent_for_session()
        self.logger.info("ProductAgent inicializado com o catálogo de dados e agente LLM.")

    def _load_catalog(self):
        """Carrega o catálogo de dados enriquecido."""
        catalog_path = "data/CATALOGO_PARA_EDICAO.json"
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Arquivo de catálogo não encontrado em {catalog_path}. O agente pode não funcionar corretamente.")
            return []
        except json.JSONDecodeError:
            self.logger.error(f"Erro ao decodificar o JSON do catálogo em {catalog_path}.")
            return []

    def search_products(self, query, limit=10):
        self.logger.info(f'Iniciando busca de produtos para a query: "{query}"')

        prompt_for_llm = self._build_prompt_for_filter_extraction(query)
        
        llm_response_raw = self.llm_agent.process_query(prompt_for_llm)
        
        llm_response_obj = llm_response_raw.get('output', llm_response_raw)

        self.logger.info(f"Resposta bruta do LLM: {llm_response_obj}")

        if isinstance(llm_response_obj, str):
            try:
                json_match = re.search(r'```json\n(.*?)```', llm_response_obj, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                else:
                    json_str = llm_response_obj.strip()
                extracted_filters = json.loads(json_str)
            except json.JSONDecodeError as e:
                self.logger.error(f"Falha ao decodificar JSON da resposta do LLM: '{llm_response_obj}'. Erro: {e}")
                return {"success": False, "message": "Não consegui entender os critérios para a busca."}
        else:
            extracted_filters = llm_response_obj

        target_file = extracted_filters.get("target_file", "ADMAT.parquet")
        filters = extracted_filters.get("filters", [])

        self.logger.info(f"Filtros extraídos: {filters} para o arquivo {target_file}")

        df = get_table_df(target_file.replace(".parquet", ""))
        if df is None:
            return {"success": False, "message": f"Arquivo de dados {target_file} não encontrado."}

        results = df
        if filters:
            for f in filters:
                col, op, val = f.get("column"), f.get("operator"), f.get("value")
                if col in results.columns:
                    try:
                        if op != 'contains':
                            results[col] = pd.to_numeric(results[col], errors='coerce')
                            val = pd.to_numeric(val)
                        
                        if op == '>': results = results[results[col] > val]
                        elif op == '<': results = results[results[col] < val]
                        elif op == '==': results = results[results[col] == val]
                        elif op == '!=': results = results[results[col] != val]
                        elif op == 'contains': results = results[results[col].astype(str).str.contains(str(val), case=False, na=False)]
                    except (ValueError, TypeError) as e:
                        self.logger.error(f"Erro ao aplicar filtro na coluna '{col}': {e}")
                        results = results[results[col].astype(str).str.contains(str(val), case=False, na=False)]
                else:
                    self.logger.warning(f"Coluna '{col}' não encontrada.")

        if results.empty:
            return {"success": False, "message": "Nenhum produto encontrado.", "data": []}

        data = results.head(limit).to_dict(orient="records")
        column_descriptions = next((item.get("column_descriptions", {}) for item in self.catalog if item.get("file_name") == target_file), {})

        return {"success": True, "data": data, "total_found": len(results), "column_descriptions": column_descriptions}

    def _build_prompt_for_filter_extraction(self, query):
        """Constrói o prompt para o LLM extrair filtros da query do usuário."""
        prompt_template = """
        Você é um especialista em análise de dados. Sua tarefa é converter a pergunta de um usuário em filtros JSON para uma busca em um DataFrame pandas.
        Use o catálogo de dados abaixo como sua única fonte de verdade sobre a estrutura dos dados.

        [CATÁLOGO DE DADOS]
        {catalog}
        
        [PERGUNTA DO USUÁRIO]
        "{query}"

        [INSTRUÇÕES]
        1. Analise a pergunta do usuário e o catálogo de dados para identificar o arquivo e as colunas mais relevantes.
        2. Para perguntas sobre vendas, priorize o arquivo `ADMAT.parquet` e use a coluna `VENDA_30D` para representar a quantidade de vendas.
        3. Converta a pergunta em uma lista de filtros JSON. Cada filtro deve ser um objeto com "column", "operator" e "value".
        4. Operadores suportados: `==` (igual a), `!=` (diferente de), `>` (maior que), `<` (menor que), `contains` (para strings).
        5. Para buscas em colunas de texto (string), sempre use o operador `contains`.
        6. Para buscas em colunas numéricas, use `==`, `!=`, `>`, `<`.
        7. **Sua resposta deve conter APENAS o código JSON, sem nenhum texto, explicação ou formatação adicional.**

        [EXEMPLO 1]
        Pergunta: "quais os produtos da categoria brinquedos com preço maior que 50?"
        Resposta JSON:
        ```json
        {{
            "target_file": "ADMAT.parquet",
            "filters": [
                {{
                    "column": "CATEGORIA",
                    "operator": "contains",
                    "value": "brinquedos"
                }},
                {{
                    "column": "PREÇO 38%",
                    "operator": ">",
                    "value": 50
                }}
            ]
        }}
        ```

        [EXEMPLO 2]
        Pergunta: "liste os itens do fabricante ACME que não sejam do grupo Papelaria"
        Resposta JSON:
        ```json
        {{
            "target_file": "ADMAT.parquet",
            "filters": [
                {{
                    "column": "FABRICANTE",
                    "operator": "contains",
                    "value": "ACME"
                }},
                {{
                    "column": "GRUPO",
                    "operator": "!=",
                    "value": "Papelaria"
                }}
            ]
        }}
        ```

        [RESPOSTA JSON]
        """
        return prompt_template.format(
            catalog=json.dumps(self.catalog, indent=2, ensure_ascii=False),
            query=query
        )

    def _simulate_llm_filter_extraction(self, query):
        """Função de simulação para demonstrar a extração de filtros. Substituir por uma chamada real ao LLM."""
        self.logger.warning("Usando extração de filtros simulada. Substituir por chamada real ao LLM.")
        if "brinquedos" in query.lower():
            return {
                "target_file": "ADMAT.parquet",
                "filters": {"CATEGORIA": "brinquedos"}
            }
        if "preço maior que 100" in query.lower():
             return {
                "target_file": "ADMAT.parquet",
                "filters": {"PRECO_38PERCENT": "> 100"} # A lógica de aplicação precisaria tratar '>'
            }
        # Simulação de busca por nome
        match = re.search(r'produtos com nome (\w+)', query, re.IGNORECASE)
        if match:
            product_name = match.group(1)
            return {
                "target_file": "ADMAT.parquet",
                "filters": {"NOME": product_name}
            }
        return {"target_file": "ADMAT.parquet", "filters": {}}

    def get_product_details(self, product_code):
        self.logger.info(f"Buscando detalhes do produto com código: {product_code}")
        filters = {"CÓDIGO": product_code}
        df = get_table_df("ADMAT", filters=filters)
        if df is None or df.empty:
            self.logger.warning(f"Produto com código {product_code} não encontrado ou arquivo Parquet ausente.")
            return {"success": False, "message": "Produto não encontrado ou arquivo Parquet ausente"}
        
        prod = df.iloc[0][
            [
                "CÓDIGO",
                "NOME",
                "PREÇO 38%",
                "FABRICANTE",
                "CATEGORIA",
                "GRUPO",
            ]
        ]
        product = {
            "codigo": prod["CÓDIGO"],
            "nome": prod["NOME"],
            "preco": prod["PREÇO 38%"],
            "fabricante": prod["FABRICANTE"],
            "categoria": prod["CATEGORIA"],
            "grupo": prod["GRUPO"],
        }
        self.logger.info(f"Detalhes do produto {product_code} encontrados: {product['nome']}")
        return {"success": True, "product": product}

    def get_columns_info(self):
        df = get_table_df("ADMAT")
        if df is None:
            return {
                "success": False,
                "message": "Arquivo Parquet da tabela ADMAT não encontrado",
            }
        columns = list(df.columns)
        dtypes = {col: str(df[col].dtype) for col in columns}
        return {"success": True, "columns": columns, "dtypes": dtypes}

    def analyze_product_performance(self, product_code):
        details = self.get_product_details(product_code)
        if not details.get("success"):
            return details
        preco = float(details["product"].get("preco", 0))
        analysis = {
            "product_id": product_code,
            "analysis": (f"Análise do produto {details['product'].get('nome', 'N/A')}"),
            "price_category": (
                "Alto" if preco > 100 else "Médio" if preco > 50 else "Baixo"
            ),
            "recommendations": [
                "Verificar estoque regularmente",
                "Monitorar preços da concorrência",
            ],
            "score": min(10, max(1, preco / 10)),
        }
        return {"success": True, "analysis": analysis}

    def get_sales_history(self, product_code):
        self.logger.info(f"Buscando histórico de vendas para o produto: {product_code}")
        
        df_admat = get_table_df("ADMAT")
        if df_admat is None or df_admat.empty:
            self.logger.warning("ADMAT.parquet não encontrado ou vazio. Não é possível gerar histórico de vendas.")
            return {"success": False, "message": "Dados de vendas não disponíveis."}

        # Encontrar a linha do produto
        product_row = df_admat[df_admat["CÓDIGO"] == product_code]
        if product_row.empty:
            self.logger.warning(f"Produto {product_code} não encontrado em ADMAT.parquet.")
            return {"success": False, "message": f"Produto {product_code} não encontrado nos dados de vendas."}
        
        product_row = product_row.iloc[0]

        sales_data = []
        # Coletar dados de vendas mensais (assumindo colunas de data)
        # Ex: '2023-05-01 00:00:00', '2023-06-01 00:00:00', etc.
        # E 'VENDA 30D' ou 'VEND. QTD 30D'
        
        # Tentativa de coletar dados de vendas mensais
        for col in df_admat.columns:
            try:
                # Tenta converter o nome da coluna para data
                date_obj = pd.to_datetime(col)
                # Verifica se é uma coluna de mês/ano e se o valor não é nulo
                if not pd.isna(product_row[col]):
                    sales_data.append({"date": date_obj.strftime("%Y-%m"), "quantity": product_row[col]})
            except ValueError:
                continue # Não é uma coluna de data
        
        # Adicionar VENDA 30D se existir e não for nulo
        if "VENDA 30D" in product_row and not pd.isna(product_row["VENDA 30D"]):
            sales_data.append({"date": "Últimos 30 Dias", "quantity": product_row["VENDA 30D"]})
        elif "VEND. QTD 30D" in product_row and not pd.isna(product_row["VEND. QTD 30D"]):
            sales_data.append({"date": "Últimos 30 Dias", "quantity": product_row["VEND. QTD 30D"]})

        if not sales_data:
            self.logger.warning(f"Nenhum dado de vendas encontrado para o produto {product_code} em ADMAT.parquet.")
            return {"success": False, "message": f"Nenhum dado de vendas encontrado para o produto {product_code}."}

        return {"success": True, "sales_history": sales_data}
