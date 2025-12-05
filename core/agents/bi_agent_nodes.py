"""
Nós (estados) para o StateGraph da arquitetura avançada do Agent_BI.
Cada função representa um passo no fluxo de processamento da consulta.
"""

import logging
import json
import re
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

# Structured logging: use project-wide helper to ensure compatibility
from core.config.logging_config import get_logger
logger = get_logger(__name__)

# Importações corrigidas baseadas na estrutura completa do projeto
from core.agent_state import AgentState
from core.llm_base import BaseLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent, _load_catalog_cached
from core.tools.data_tools import fetch_data_from_query
from core.connectivity.parquet_adapter import ParquetAdapter
from core.utils.json_utils import _clean_json_values

def _extract_user_query(state: AgentState) -> str:
    """Concatena o conteúdo de todas as mensagens em uma única string para contexto completo."""
    full_conversation = []
    for msg in state.get('messages', []):
        role = "User" if getattr(msg, 'type', 'user') == 'user' else "Assistant"
        content = getattr(msg, 'content', '')
        if isinstance(content, dict): # Caso de content aninhado
            content = content.get("content", str(content))
        full_conversation.append(f"{role}: {content}")
    return "\n".join(full_conversation)

def format_mc_response(result: Dict[str, Any]) -> str:
    """
    ✅ OTIMIZAÇÃO v2.2: Formata resposta de MC com markdown limpo (sem caracteres especiais)

    Args:
        result: Dicionário com dados do produto retornado por calcular_mc_produto

    Returns:
        String formatada em markdown para renderização perfeita no Streamlit
    """
    # ✅ Formatação limpa usando markdown (renderiza perfeitamente no Streamlit)
    response_text = f"""
### 📦 PRODUTO: {result['nome']}

**Informações Básicas:**
- **Segmento:** {result['segmento']}
- **UNE:** {result['une_id']}

---

### 📊 INDICADORES

- 📈 **MC Calculada:** {result['mc_calculada']:.0f} unidades/dia
- 📦 **Estoque Atual:** {result['estoque_atual']:.0f} unidades
- 🟢 **Linha Verde:** {result['linha_verde']:.0f} unidades
- 📊 **Percentual da LV:** {result['percentual_linha_verde']:.1f}%

---

### ⚠️ RECOMENDAÇÃO

**{result['recomendacao']}**
"""

    return response_text

def format_abastecimento_response(result: Dict[str, Any]) -> str:
    """
    Formata a resposta de abastecimento no padrão ideal de apresentação.

    Args:
        result: Dicionário com lista de produtos retornado por calcular_abastecimento_une

    Returns:
        String formatada no padrão ideal de apresentação
    """
    une_id = result.get('une_id', 'N/A')
    segmento = result.get('segmento', 'Todos')
    total_produtos = result.get('total_produtos', 0)
    produtos = result.get('produtos', [])

    # Cabeçalho
    response_text = f"""Produtos que Precisam Abastecimento

UNE: {une_id}
Segmento: {segmento}
Total de Produtos: {total_produtos}

"""

    # Se não há produtos, mensagem específica
    if total_produtos == 0:
        response_text += "[OK] Nenhum produto precisa de abastecimento no momento."
        return response_text

    # Lista os top produtos (máximo 10 para não poluir)
    response_text += "Top Produtos:\n\n"

    for idx, prod in enumerate(produtos[:10], 1):
        nome = prod.get('nome_produto', 'N/A')[:40]  # Truncar nome se muito longo
        estoque = prod.get('estoque_atual', 0)
        linha_verde = prod.get('linha_verde', 0)
        qtd_abastecer = prod.get('qtd_a_abastecer', 0)
        percentual = prod.get('percentual_estoque', 0)

        response_text += f"{idx}. {nome}\n"
        response_text += f"   Estoque: {estoque:.0f} un | LV: {linha_verde:.0f} | Abastecer: {qtd_abastecer:.0f} un ({percentual:.1f}% da LV)\n\n"

    if total_produtos > 10:
        response_text += f"\n... e mais {total_produtos - 10} produtos."

    return response_text

def format_preco_response(result: Dict[str, Any]) -> str:
    """
    Formata a resposta de cálculo de preço no padrão ideal de apresentação.

    Args:
        result: Dicionário com cálculo de preço retornado por calcular_preco_final_une

    Returns:
        String formatada no padrão ideal de apresentação
    """
    valor_original = result.get('valor_original', 0)
    tipo = result.get('tipo', 'N/A')
    ranking = result.get('ranking', 0)
    desconto_ranking = result.get('desconto_ranking', '0%')
    forma_pagamento = result.get('forma_pagamento', 'N/A')
    desconto_pagamento = result.get('desconto_pagamento', '0%')
    preco_final = result.get('preco_final', 0)
    economia = result.get('economia', 0)
    percentual_economia = result.get('percentual_economia', 0)

    # Determinar limite de tipo
    limite_tipo = ">= R$ 750,00" if tipo == "Atacado" else "< R$ 750,00"
    if tipo == "Único":
        limite_tipo = "(Preco unico)"

    response_text = f"""Calculo de Preco Final UNE

Valor Original: R$ {valor_original:,.2f}
Tipo de Venda: {tipo} {limite_tipo}

Descontos:
- Ranking {ranking}: {desconto_ranking}
- Pagamento ({forma_pagamento}): {desconto_pagamento}

Desconto Total: {percentual_economia:.1f}%

PRECO FINAL: R$ {preco_final:,.2f}
Economia: R$ {economia:,.2f} ({percentual_economia:.1f}%)"""

    return response_text

def format_produtos_sem_vendas_response(result: Dict[str, Any]) -> str:
    """
    Formata a resposta de produtos sem vendas no padrão ideal de apresentação.

    Args:
        result: Dicionário com lista de produtos retornado por calcular_produtos_sem_vendas

    Returns:
        String formatada no padrão ideal de apresentação
    """
    from core.config.une_mapping import get_une_name

    une_id = result.get('une_id', 'N/A')
    total_produtos = result.get('total_produtos', 0)
    produtos = result.get('produtos', [])
    criterio = result.get('criterio', 'VENDA_30DD = 0')
    recomendacao = result.get('recomendacao', '')

    # Resolver nome da UNE
    une_name = get_une_name(str(une_id)) if une_id != 'N/A' else 'N/A'
    une_display = f"{une_name} (UNE {une_id})" if une_name != 'N/A' else str(une_id)

    # Calcular estatísticas
    estoque_total_parado = sum([p.get('estoque_atual', 0) for p in produtos])

    # Identificar produtos críticos (estoque alto)
    produtos_criticos = [p for p in produtos if p.get('estoque_atual', 0) > 1000]

    # Cabeçalho com estatísticas
    response_text = f"""# 🔴 Produtos Sem Vendas (Sem Giro)

---

### 📍 **{une_display}**

| Métrica | Valor |
|---------|-------|
| 📦 **Total de Produtos** | **{total_produtos:,}** produtos |
| 🏭 **Estoque Parado** | **{estoque_total_parado:,.0f}** unidades |
| ⚠️ **Produtos Críticos** | **{len(produtos_criticos)}** (estoque > 1000 un) |
| 📊 **Critério** | {criterio} |

---

"""

    # Se não há produtos
    if total_produtos == 0:
        response_text += """
### ✅ Situação Ideal

**Nenhum produto sem vendas encontrado!**

Todos os produtos com estoque apresentam movimento nos últimos 30 dias.
"""
        return response_text

    # Análise rápida
    if len(produtos_criticos) > 0:
        response_text += f"""
### ⚠️ Alerta Crítico

**{len(produtos_criticos)} produtos** com estoque alto (> 1000 un) estão **parados há mais de 30 dias**.

💡 **Ação Recomendada:** Priorizar estes produtos para ação promocional ou transferência.

---

"""

    # Lista os top produtos (máximo 10 para não poluir)
    response_text += f"### 🔝 Top {min(10, total_produtos)} Produtos Mais Críticos\n\n"
    response_text += "_Ordenado por quantidade de estoque parado_\n\n"

    for idx, prod in enumerate(produtos[:10], 1):
        codigo = prod.get('codigo', 'N/A')
        nome = prod.get('nome_produto', 'N/A')[:50]  # Truncar nome
        segmento = prod.get('segmento', 'N/A')
        estoque = prod.get('estoque_atual', 0)
        linha_verde = prod.get('linha_verde', 0)

        # Emoji de criticidade baseado em estoque
        emoji_criticidade = "🔥" if estoque > 10000 else "⚠️" if estoque > 1000 else "📦"

        # Card do produto
        response_text += f"""
<details>
<summary><b>{idx}. {emoji_criticidade} [{codigo}]</b> {nome}</summary>

- **Segmento:** {segmento}
- **Estoque Parado:** {estoque:,.0f} unidades
- **Linha Verde:** {linha_verde:,.0f} unidades
- **Status:** 🔴 Sem vendas há > 30 dias
- **Criticidade:** {'MUITO ALTA' if estoque > 10000 else 'ALTA' if estoque > 1000 else 'MÉDIA'}

</details>

"""

    if total_produtos > 10:
        response_text += f"\n_📋 Exibindo 10 de {total_produtos:,} produtos. {total_produtos - 10:,} produtos adicionais não exibidos._\n"

    # Análise de segmentos se disponível
    if produtos:
        segmentos = {}
        for p in produtos[:50]:  # Analisar top 50
            seg = p.get('segmento', 'Sem Segmento')
            segmentos[seg] = segmentos.get(seg, 0) + 1

        if len(segmentos) > 1:
            top_segmentos = sorted(segmentos.items(), key=lambda x: x[1], reverse=True)[:5]
            response_text += f"""
---

### 📊 Distribuição por Segmento (Top 5)

"""
            for seg, qtd in top_segmentos:
                percentual = (qtd / len(produtos[:50])) * 100
                barra = "█" * int(percentual / 5)  # Barra visual
                response_text += f"- **{seg}:** {qtd} produtos ({percentual:.1f}%) {barra}\n"

    # Recomendação
    response_text += f"""

---

### 💡 Recomendações de Ação

"""

    if len(produtos_criticos) > 10:
        response_text += f"""
#### ⚡ Prioridade URGENTE
- **{len(produtos_criticos)} produtos** com estoque > 1000 unidades parados
- **Ação:** Campanhas promocionais agressivas ou transferência para UNEs com demanda

"""

    if recomendacao:
        response_text += f"#### 📋 Análise Geral\n{recomendacao}\n\n"

    response_text += """
#### 🎯 Sugestões Práticas
1. **Transferências:** Verificar UNEs com demanda usando `sugerir_transferencias_automaticas`
2. **Promoções:** Criar campanhas para produtos com maior estoque parado
3. **Reavaliação:** Considerar descontinuar produtos sem movimento há > 90 dias
4. **Reposicionamento:** Verificar se produtos estão em local visível na loja

"""

    return response_text

from core.factory.component_factory import ComponentFactory

# A fábrica pode ser instanciada aqui ou injetada (ver melhores práticas)
_factory = ComponentFactory()


def classify_intent(state: AgentState) -> Dict[str, Any]:
    """
    Classifica a intenção do utilizador usando Few-Shot Learning.

    Baseado em: Context7 - Few-Shot Learning + Confidence Scoring

    Intenções possíveis:
    - 'une_operation': Operações UNE (abastecimento, MC, preços)
    - 'python_analysis': Análise complexa SEM visualização
    - 'gerar_grafico': Visualizações e gráficos
    - 'resposta_simples': Consultas simples de filtro
    """
    llm_adapter = _factory.get_intent_classification_llm()
    if not llm_adapter:
        logger.error("Não foi possível obter o LLM para classificação de intenção.")
        return {"intent": "error", "plan": {"intent": "error"}}
    user_query = _extract_user_query(state)
    logger.info(f"[NODE] classify_intent: Recebida query '{user_query}'")

    # ⚡ OTIMIZAÇÃO: Few-shot examples reduzidos (13→6 exemplos, -50% tokens)
    # Removidos campos confidence/reasoning desnecessários
    few_shot_examples = [
        # une_operation - 2 exemplos mais representativos
        {"query": "mc do produto 704559 na une scr", "intent": "une_operation"},
        {"query": "quais produtos precisam abastecimento na UNE MAD", "intent": "une_operation"},
        # gerar_grafico - 2 exemplos mais representativos
        {"query": "gere um gráfico de vendas por categoria", "intent": "gerar_grafico"},
        {"query": "mostre a evolução de vendas mensais", "intent": "gerar_grafico"},
        # python_analysis - 1 exemplo representativo
        {"query": "qual produto mais vende no segmento tecidos", "intent": "python_analysis"},
        # resposta_simples - 1 exemplo representativo
        {"query": "liste os produtos da categoria AVIAMENTOS", "intent": "resposta_simples"}
    ]

    # ⚡ OTIMIZAÇÃO: Prompt simplificado (-40% tokens)
    prompt = f"""Classifique a intenção do usuário em um sistema de análise de varejo.

EXEMPLOS:
{json.dumps(few_shot_examples, indent=2, ensure_ascii=False)}

CATEGORIAS:
- une_operation: Operações UNE (abastecimento, MC, preços)
- python_analysis: Análise/ranking sem visualização
- gerar_grafico: Gráficos, tendências, visualizações
- resposta_simples: Consultas básicas de filtro

QUERY: "{user_query}"

Retorne JSON:
{{
  "intent": "categoria",
  "confidence": 0.95,
  "reasoning": "breve explicação"
}}"""

    # 🔍 LOGGING DETALHADO - Diagnóstico de classificação
    logger.info(f"[CLASSIFY_INTENT] 📝 Query original: '{user_query}'")

    # Use json_mode=True para forçar a resposta em JSON
    # 🔥 NOVO: Passar contexto ao cache para separar cache de classify_intent
    cache_context = {"operation": "classify_intent", "query_type": "intent_classification"}
    response_dict = llm_adapter.get_completion(
        messages=[{"role": "user", "content": prompt}],
        json_mode=True,
        cache_context=cache_context
    )
    plan_str = response_dict.get("content", "{}")

    # 🔍 LOGGING: Resposta raw da LLM
    logger.info(f"[CLASSIFY_INTENT] 🤖 Resposta LLM raw: {plan_str[:200]}...")

    # Fallback para extrair JSON de blocos de markdown
    if "```json" in plan_str:
        match = re.search(r"```json\n(.*?)```", plan_str, re.DOTALL)
        if match:
            plan_str = match.group(1).strip()

    try:
        plan = json.loads(plan_str)
    except json.JSONDecodeError:
        logger.warning(f"Não foi possível decodificar o JSON da intenção: {plan_str}")
        # Fallback para a intenção mais poderosa em caso de erro de parsing
        plan = {"intent": "python_analysis", "entities": {}}

    intent = plan.get('intent', 'python_analysis')
    confidence = plan.get('confidence', 0.5)
    reasoning = plan.get('reasoning', 'Não fornecido')

    # ✅ NOVO: Validação de confidence score (Context7 best practice)
    if confidence < 0.7:
        logger.warning(f"[CLASSIFY_INTENT] ⚠️ Baixa confiança na classificação: {confidence:.2f}")
        logger.warning(f"[CLASSIFY_INTENT] Reasoning: {reasoning}")
        # TODO: Futuramente, pode pedir clarificação ao usuário aqui

    # 🔍 LOGGING DETALHADO - Intent final com confidence
    logger.info(f"[CLASSIFY_INTENT] ✅ Intent: '{intent}' | Confidence: {confidence:.2f} | Reasoning: {reasoning}")

    # 🔍 LOGGING: Alertar se query pede gráfico mas não foi classificada como tal
    keywords_visuais = ['gráfico', 'chart', 'visualização', 'evolução', 'tendência', 'distribuição', 'sazonalidade', 'comparar']
    query_lower = user_query.lower()
    tem_keyword_visual = any(kw in query_lower for kw in keywords_visuais)

    if tem_keyword_visual and intent != 'gerar_grafico':
        logger.warning(f"[CLASSIFY_INTENT] ⚠️ POSSÍVEL ERRO: Query tem palavra visual ({[kw for kw in keywords_visuais if kw in query_lower]}) mas intent='{intent}' (não 'gerar_grafico')")

    logger.info(f"[NODE] classify_intent: Intenção classificada como '{intent}'")
    
    # Assegura que o plan sempre tenha a chave 'intent'
    if 'intent' not in plan:
        plan['intent'] = intent
        
    return {"plan": plan, "intent": intent}



def generate_parquet_query(state: AgentState, parquet_adapter: ParquetAdapter) -> Dict[str, Any]:
    """
    Gera um dicionário de filtros para consulta Parquet a partir da pergunta do utilizador, usando o schema do arquivo Parquet e descrições de colunas.
    """
    llm_adapter = _factory.get_code_generation_llm()
    if not llm_adapter:
        logger.error("Não foi possível obter o LLM para geração de query Parquet.")
        return {"parquet_filters": {}, "final_response": {"type": "error", "content": "Erro interno de configuração do LLM."}}
    user_query = _extract_user_query(state)
    logger.info(f"[NODE] generate_parquet_query: Gerando filtros para '{user_query}'")

    # Importar field_mapper
    from core.utils.field_mapper import get_field_mapper
    
    # Obter o schema do arquivo Parquet para dar contexto ao LLM
    try:
        schema = parquet_adapter.get_schema()
    except Exception as e:
        logger.error(f"Erro ao obter o schema do arquivo Parquet: {e}", exc_info=True)
        return {"parquet_filters": {}, "final_response": {"type": "error", "content": "Não foi possível aceder ao schema do arquivo Parquet para gerar a consulta."}}

    # ⚡ OTIMIZAÇÃO: Usar cache de catálogo em vez de carregar toda vez
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    catalog_file_path = os.path.join(base_dir, "data", "catalog_focused.json")

    try:
        catalog_data = _load_catalog_cached()
        
        # Find the entry for admatao.parquet
        admatao_catalog = next((entry for entry in catalog_data if entry.get("file_name") == "admatao.parquet"), None)
        
        if admatao_catalog and "column_descriptions" in admatao_catalog:
            column_descriptions = admatao_catalog["column_descriptions"]
            column_descriptions_str = json.dumps(column_descriptions, indent=2, ensure_ascii=False)
        else:
            column_descriptions_str = "Nenhuma descrição de coluna disponível."
            logger.warning("Descrições de coluna para admatao.parquet não encontradas no catálogo.")

    except FileNotFoundError:
        column_descriptions_str = "Erro: Arquivo de catálogo não encontrado."
        logger.error(f"Arquivo de catálogo não encontrado em {catalog_file_path}", exc_info=True)
    except Exception as e:
        column_descriptions_str = f"Erro ao carregar descrições de coluna: {e}"
        logger.error(f"Erro ao carregar descrições de coluna: {e}", exc_info=True)
    
    # ✅ CONTEXT7: Adicionar required_columns ao estado se for gráfico de evolução
    required_columns = []
    if state.get("intent") == "gerar_grafico":
        query_lower = user_query.lower()
        if any(kw in query_lower for kw in ['evolução', 'evolucao', 'tendência', 'tendencia', 'meses', 'histórico', 'historico']):
            required_columns = ['codigo', 'une_nome'] + [f'mes_{i:02d}' for i in range(1, 13)]
            logger.info(f"Gráfico de evolução detectado. Adicionando required_columns: {required_columns}")

    # Inicializar field_mapper
    field_mapper = get_field_mapper(catalog_file_path)
    
    # Gerar mapeamento de campos para o prompt
    field_mapping_guide = """
## Mapeamento de Campos (OBRIGATÓRIO)

Quando o usuário mencionar:
- "segmento" → use: NOMESEGMENTO
- "categoria" → use: NomeCategoria
- "grupo" → use: NOMEGRUPO
- "subgrupo" → use: NomeSUBGRUPO
- "código" ou "produto" → use: PRODUTO
- "nome" → use: NOME
- "estoque" → use: ESTOQUE_UNE
- "preço" → use: LIQUIDO_38
- "vendas" ou "vendas 30 dias" → use: VENDA_30DD
- "fabricante" → use: NomeFabricante

**REGRAS CRÍTICAS:**
1. NUNCA use "SEGMENTO", sempre use "NOMESEGMENTO"
2. NUNCA use "CATEGORIA", sempre use "NomeCategoria"
3. NUNCA use "CODIGO", sempre use "PRODUTO"
4. Para estoque zero: filtre por ESTOQUE_UNE = 0
5. Para campos de texto: use valores em MAIÚSCULAS
"""


    prompt = f"""
    Você é um especialista em traduzir o histórico de uma conversa em filtros de dados JSON. Sua tarefa é analisar a **conversa completa** e convertê-la em um objeto JSON de filtros, usando o schema e as regras de mapeamento fornecidas.

    {field_mapping_guide}

    **Instruções Críticas:**
    1.  **FOCO NA CONVERSA COMPLETA:** Sua resposta DEVE ser uma tradução da conversa completa. Considere as perguntas e respostas anteriores para resolver ambiguidades.
    2.  **EXTRAÇÃO DE CÓDIGOS:** Se a conversa contiver um número que se pareça com um código de produto (geralmente com 5 ou mais dígitos), você DEVE extraí-lo como um filtro para a coluna `PRODUTO`.
    3.  **NÃO COPIE OS EXEMPLOS:** Os exemplos abaixo são apenas um guia de estilo e formato. Não os use como base para a sua resposta.
    4.  **GERE APENAS JSON:** Sua saída final deve ser um único e válido objeto JSON, sem nenhum texto ou explicação adicional.
    5.  **CONSULTA VAZIA:** Se a conversa não contiver nenhum filtro (ex: "liste todas as categorias"), retorne um objeto JSON vazio: `{{}}`.

    **Schema do Arquivo Parquet (para referência de colunas):**
    ```
    {schema}
    ```

    ---

    **Exemplos de Formato (Use apenas como guia):**

    - **Exemplo 1 (Filtro de Código de Produto):**
      - Conversa: "User: qual o estoque do produto 369947?"
      - Filtros JSON: `{{"PRODUTO": 369947}}`

    - **Exemplo 2 (Filtro Composto com Esclarecimento):**
      - Conversa: "User: me mostre as vendas\nAssistant: Claro, vendas em valor ou quantidade?\nUser: quantidade"
      - Filtros JSON: `{{"VENDA_30DD": {{">": 0}}}}` (exemplo, a lógica exata depende do LLM)
    
    - **Exemplo 3 (Filtro de Texto):**
      - Conversa: "User: liste produtos da categoria aviamentos"
      - Filtros JSON: `{{"NomeCategoria": "AVIAMENTOS"}}`

    ---

    **Conversa Completa (TRADUZIR ESTA):**
    "{user_query}"

    **Filtros JSON Resultantes:**
    """

    # 🔥 NOVO: Passar contexto ao cache para separar queries Parquet
    cache_context = {"operation": "generate_parquet_query", "query_type": "filter_generation", "intent": state.get("intent")}
    response_dict = llm_adapter.get_completion(
        messages=[{"role": "user", "content": prompt}],
        json_mode=True,
        cache_context=cache_context
    )
    filters_str = response_dict.get("content", "{}").strip()

    # Fallback para extrair JSON de blocos de markdown
    if "```json" in filters_str:
        match = re.search(r"```json\n(.*?)```", filters_str, re.DOTALL)
        if match:
            filters_str = match.group(1).strip()

    try:
        parquet_filters = json.loads(filters_str)
    except json.JSONDecodeError:
        logger.warning(f"Não foi possível decodificar o JSON dos filtros Parquet: {filters_str}")
        parquet_filters = {}

    # ✅ MAPEAMENTO DE COLUNAS: LLM usa nomes padronizados, Parquet tem nomes reais
    column_mapping = {
        'PRODUTO': 'codigo',
        'NOME': 'nome_produto',
        'NOMESEGMENTO': 'nomesegmento',
        'NomeCategoria': 'NOMECATEGORIA',
        'NOMEGRUPO': 'nomegrupo',
        'NomeSUBGRUPO': 'NOMESUBGRUPO',
        'VENDA_30DD': 'venda_30_d',
        'ESTOQUE_UNE': 'estoque_atual',
        'LIQUIDO_38': 'preco_38_percent',
        'UNE_NOME': 'une_nome',
        'NomeFabricante': 'NOMEFABRICANTE'
    }

    # Aplicar mapeamento nos filtros
    mapped_filters = {}
    for key, value in parquet_filters.items():
        mapped_key = column_mapping.get(key, key)
        mapped_filters[mapped_key] = value

    logger.info(f"Filtros originais: {parquet_filters}")
    logger.info(f"Filtros mapeados: {mapped_filters}")

    return {"parquet_filters": mapped_filters, "required_columns": required_columns}


def execute_query(state: AgentState, parquet_adapter: ParquetAdapter, required_columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Executa os filtros Parquet do estado.
    """
    user_query = _extract_user_query(state)
    parquet_filters = state.get('parquet_filters', {})
    required_columns_from_state = state.get('required_columns', None) # Retrieve from state

    logger.info(f"[NODE] execute_query: Executando com filtros {parquet_filters}")
    logger.info(f"📊 QUERY EXECUTION - User query: '{user_query}'")
    logger.info(f"📊 QUERY EXECUTION - Filters: {parquet_filters}")
    logger.info(f"📊 QUERY EXECUTION - Required Columns: {required_columns_from_state}")

    # A lógica de fallback para filtros vazios foi removida, pois era a causa do MemoryError.
    # Agora, a proteção no ParquetAdapter será acionada se os filtros estiverem vazios.
    retrieved_data = fetch_data_from_query.invoke({"query_filters": parquet_filters, "parquet_adapter": parquet_adapter, "required_columns": required_columns_from_state})

    # ✅ LOG DETALHADO DOS RESULTADOS
    if isinstance(retrieved_data, list):
        if retrieved_data and isinstance(retrieved_data[0], dict) and "error" in retrieved_data[0]:
            logger.error(f"❌ QUERY ERROR: {retrieved_data[0]}")
        else:
            logger.info(f"✅ QUERY SUCCESS: Retrieved {len(retrieved_data)} rows")
            if retrieved_data and isinstance(retrieved_data[0], dict):
                logger.info(f"📋 SAMPLE DATA COLUMNS: {list(retrieved_data[0].keys())}")
            elif retrieved_data:
                logger.warning(f"⚠️ First item is not dict: {type(retrieved_data[0])}")
    else:
        logger.warning(f"⚠️ UNEXPECTED DATA TYPE: {type(retrieved_data)}")

    return {"retrieved_data": retrieved_data}

def generate_plotly_spec(state: AgentState, code_gen_agent: CodeGenAgent) -> Dict[str, Any]:
    """
    Gera uma especificação JSON para Plotly ou uma resposta textual usando o CodeGenAgent.
    Este nó agora lida com dois cenários:
    1.  **Com `raw_data`**: Gera um gráfico a partir de dados pré-filtrados.
    2.  **Sem `raw_data` (fluxo `python_analysis`)**: Gera um script Python para fazer a análise completa (filtrar, agregar, etc.).
    """
    llm_adapter = _factory.get_code_generation_llm()
    if not llm_adapter:
        logger.error("Não foi possível obter o LLM para geração de especificação Plotly.")
        return {"final_response": {"type": "error", "content": "Erro interno de configuração do LLM."}}
    
    # Garante que o code_gen_agent use o LLM correto
    code_gen_agent.llm = llm_adapter
    logger.info("Nó: generate_plotly_spec")
    raw_data = state.get("retrieved_data")
    user_query = _extract_user_query(state)
    plan = state.get("plan", {})
    intent = plan.get("intent")

    logger.info(f"🐍 Python CodeGen - User query: '{user_query}'")
    logger.info(f"🐍 Python CodeGen - Intent: {intent}")
    logger.info(f"🐍 Python CodeGen - Data available: {len(raw_data) if raw_data else 'No pre-loaded data'}")

    # Verifica se o estado de erro já foi definido por um nó anterior
    if raw_data and isinstance(raw_data, list) and len(raw_data) > 0 and isinstance(raw_data[0], dict) and "error" in raw_data[0]:
        return {"final_response": {"type": "text", "content": raw_data[0]["error"]}}

    try:
        # ⚡ OTIMIZAÇÃO: Carregar catálogo do cache
        catalog_context = ""
        try:
            catalog_data = _load_catalog_cached()

            catalog_context = "## Entidades de Negócio (Segmentos e Fabricantes)\n\n"
            catalog_context += "Para interpretar a query, use o seguinte contexto:\n\n"

            if "nomesegmento" in catalog_data:
                catalog_context += f"### Segmentos (coluna 'nomesegmento')\n"
                catalog_context += f"- **Descrição**: {catalog_data['nomesegmento']['description']}\n"
                catalog_context += f"- **Exemplos**: {', '.join(catalog_data['nomesegmento']['examples'][:5])}...\n\n"

            if "NOMEFABRICANTE" in catalog_data:
                catalog_context += f"### Fabricantes (coluna 'NOMEFABRICANTE')\n"
                catalog_context += f"- **Descrição**: {catalog_data['NOMEFABRICANTE']['description']}\n"
                catalog_context += f"- **Exemplos**: {', '.join(catalog_data['NOMEFABRICANTE']['examples'][:5])}...\n\n"

            catalog_context += "**REGRA DE OURO PARA FILTROS:**\n"
            catalog_context += "1. Se o usuário mencionar algo como 'tecidos', 'papelaria', 'artesanato', use a coluna `nomesegmento`.\n"
            catalog_context += "2. Se o usuário mencionar uma marca ou fornecedor como 'KIT', 'EURO ROMA', 'LINEA', 'CÍRCULO', use a coluna `NOMEFABRICANTE`.\n"
            catalog_context += "3. Na dúvida, verifique se o termo da query está na lista de exemplos de `NOMEFABRICANTE`.\n"
        except Exception as e:
            logger.error(f"❌ Erro ao carregar o arquivo de catálogo: {e}")


        # Cenário 1: Análise complexa, sem dados pré-carregados.
        # O CodeGenAgent deve fazer o trabalho completo.
        if not raw_data:
            prompt_for_code_gen = f"""
            {catalog_context}
            **TAREFA:** Você deve escrever um script Python para responder à pergunta do usuário.

            **INSTRUÇÕES OBRIGATÓRIAS:**
            1. **CARREGUE OS DADOS:** Inicie seu script com a linha: `df = load_data()`
            2. **RESPONDA À PERGUNTA:** Usando o dataframe `df`, escreva o código para responder à seguinte pergunta: "{user_query}"
            3. **SALVE O RESULTADO NA VARIÁVEL `result`:** A última linha do seu script DEVE ser a atribuição do resultado final à variável `result`. Esta é a única forma que o sistema tem para ver sua resposta. NÃO use `print()`.

            **REGRAS OBRIGATÓRIAS:**
            0. **🚨 CRÍTICO: Última linha deve ser SEMPRE `result = <Plotly Figure ou DataFrame>` - NUNCA retorne dicionário de erro!**
            1. **SEMPRE defina variáveis antes de usar:** Se usar `produto_id`, defina antes (ex: `produto_id = 369947`)
            2. **Produtos em Excesso:** Filtre `estoque_atual > linha_verde`
            3. **"linha verde" NÃO é segmento:** É uma COLUNA (linha_verde) que indica meta de estoque
            4. **Produtos que precisam ajuste na linha verde:** Filtre onde `estoque_atual != linha_verde`
            5. **UNE:** Filtre por `une_nome` (ex: 'BON', 'TAQ', 'TIJ'), NÃO por código numérico
            6. **Análise Temporal:** Dataset TEM APENAS venda_30_d (últimos 30 dias) - NÃO EXISTEM colunas mes_01, mes_02... mes_12!
            7. **"em todas as UNEs":** Use merge para incluir UNEs com venda = 0
            8. **Top N:** Use `.head(N)` após ordenar, ou `.nlargest(N, coluna)`
            9. **Gráficos de tendência temporal:** Use venda_30_d como métrica - é a ÚNICA disponível para vendas. Para comparativo entre segmentos/produtos, agrupar por nomesegmento/NOMEFABRICANTE e somar venda_30_d
            10. **Se não tiver dados:** SEMPRE criar uma Figure Plotly com mensagem de aviso (use `go.Figure()` com `add_annotation()`) - NÃO retorne dict de erro!

            **COLUNAS REAIS DISPONÍVEIS:**
            - `codigo` - Código do produto
            - `nome_produto` - Nome do produto
            - `une_nome` - Nome da UNE
            - `nomesegmento` - Segmento (ex: 'TECIDOS', 'ARMARINHO E CONFECÇÃO')
            - `NOMEFABRICANTE` - Fabricante/Marca
            - `venda_30_d` - Vendas últimos 30 dias (ÚNICA métrica temporal disponível!)
            - `estoque_atual` - Estoque em estoque
            - `linha_verde` - Meta de estoque (line verde)
            - `preco_38_percent` - Preço venda
            - `nomegrupo` - Grupo do produto
            
            **Não usar estas colunas (NÃO EXISTEM):**
            ❌ `mes_01`, `mes_02`, ... `mes_12` - ESTAS COLUNAS NÃO EXISTEM!
            ❌ Qualquer coluna com padrão mes_*
            ❌ `mês`, `month`, `data_venda`, `período`

            **Exemplo 1 - Top 10 produtos por UNE:**
            ```python
            df = load_data()
            # Filtrar UNE (use nome em maiúsculas)
            df_une = df[df['une_nome'].str.upper() == 'TIJ']
            # Top 10 por vendas
            top10 = df_une.nlargest(10, 'venda_30_d')[['nome_produto', 'venda_30_d']]
            result = top10
            ```

            **Exemplo 2 - Produtos precisando ajuste na linha verde:**
            ```python
            df = load_data()
            # Filtrar UNE
            df_une = df[df['une_nome'].str.upper() == 'BON']
            # linha_verde é COLUNA, não segmento!
            df_ajuste = df_une[df_une['estoque_atual'] != df_une['linha_verde']]
            result = df_ajuste[['nome_produto', 'estoque_atual', 'linha_verde']]
            ```

            **Exemplo 3 - Segmentos por vendas (NÃO há dados temporais):**
            ```python
            df = load_data()
            # Filtrar UNE
            df_une = df[df['une_nome'].str.upper() == 'TAQ']
            # Agrupar por segmento (só temos venda_30_d, sem histórico mensal!)
            segmentos = df_une.groupby('nomesegmento')['venda_30_d'].sum().sort_values(ascending=False)
            result = segmentos.reset_index()
            ```

            **Exemplo 4 - GRÁFICO COMPARATIVO (sempre retornar Figure Plotly):**
            ```python
            import plotly.express as px
            import plotly.graph_objects as go
            df = load_data()
            
            # Filtrar dados
            df_filtered = df[df['nomesegmento'] == 'TECIDOS'].copy()
            
            # ✅ VALIDAÇÃO CRÍTICA: Se não tiver dados, criar gráfico de aviso
            if len(df_filtered) == 0:
                # Em vez de retornar dicionário de erro, criar gráfico que mostre a mensagem
                fig = go.Figure()
                fig.add_annotation(
                    text="❌ Nenhum dado encontrado para essa query",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16, color="red")
                )
                fig.update_layout(title="Aviso: Sem Dados", xaxis_visible=False, yaxis_visible=False)
                result = fig
            else:
                # Agrupar e criar gráfico
                agg_data = df_filtered.groupby('NOMEFABRICANTE')['venda_30_d'].sum().sort_values(ascending=False).head(10)
                fig = px.bar(
                    x=agg_data.index, 
                    y=agg_data.values,
                    title='Comparativo de Vendas TECIDOS',
                    labels={{'x': 'Fabricante', 'y': 'Total Vendido (30 dias)'}}
                )
                result = fig
            ```



            **Seu Script Python (Lembre-se, a última linha deve ser `result = ...`):**
            """
        # Cenário 2: Geração de gráfico a partir de dados pré-carregados.
        else:
            prompt_for_code_gen = f"""
            Com base na consulta do usuário e no DataFrame Pandas `df_raw_data` já disponível, gere um script Python para criar um gráfico com Plotly Express.
            O objeto da figura Plotly resultante deve ser armazenado em uma variável chamada `result`.
            Não inclua `fig.show()`.

            **Consulta do Usuário:** "{user_query}"
            **Dados Brutos (amostra):**
            ```json
            {pd.DataFrame(raw_data).head(3).to_json(orient="records", indent=2)}
            ```

            **Seu Script Python:**
            """

        # O CodeGenAgent espera um dicionário com a query e os dados brutos (se existirem)
        code_gen_input = {
            "query": prompt_for_code_gen,
            "raw_data": raw_data  # Passa os dados brutos ou None
        }
        
        logger.info(f"\n--- PROMPT PARA CODEGENAGENT ---\n{prompt_for_code_gen}\n---------------------------------")

        logger.info("🚀 Calling code_gen_agent.generate_and_execute_code...")
        code_gen_response = code_gen_agent.generate_and_execute_code(code_gen_input)

        # ✅ LOGS DETALHADOS DO RETORNO DO CODEGENAGENT
        logger.info(f"📋 CodeGenAgent response type: {code_gen_response.get('type')}")
        logger.info(f"📋 CodeGenAgent response keys: {list(code_gen_response.keys())}")

        # Logs específicos por tipo
        if code_gen_response.get("type") == "dataframe":
            df_result = code_gen_response.get("output")
            if isinstance(df_result, pd.DataFrame):
                logger.info(f"📊 DataFrame result: {len(df_result)} rows, {len(df_result.columns)} cols")
                logger.info(f"📊 DataFrame columns: {list(df_result.columns)}")
                if len(df_result) > 0:
                    logger.info(f"📊 DataFrame sample (first 3 rows): {df_result.head(3).to_dict(orient='records')}")
            else:
                logger.warning(f"⚠️ Expected DataFrame but got {type(df_result)}")
        elif code_gen_response.get("type") == "text":
            text_output = str(code_gen_response.get("output"))
            logger.info(f"📝 Text result length: {len(text_output)} chars")
            logger.info(f"📝 Text result preview: {text_output[:200]}...")

        # Processa a resposta do CodeGenAgent
        if code_gen_response.get("type") == "chart":
            plotly_spec = json.loads(code_gen_response.get("output"))
            logger.info(f"📈 Chart generated successfully")
            return {"plotly_spec": plotly_spec}

        elif code_gen_response.get("type") == "multiple_charts":
            # ✅ CORREÇÃO: Múltiplos gráficos Plotly
            charts_json_list = code_gen_response.get("output")
            logger.info(f"📈 {len(charts_json_list)} charts generated successfully")

            # Retornar como final_response com tipo especial
            return {
                "final_response": {
                    "type": "multiple_charts",
                    "content": charts_json_list,
                    "user_query": user_query
                }
            }

        elif code_gen_response.get("type") == "dataframe":
            # ✅ CORREÇÃO: Converter DataFrame para lista de dicionários
            df_result = code_gen_response.get("output")

            # Garantir que seja DataFrame ou lista
            if isinstance(df_result, pd.DataFrame):
                data_list = df_result.to_dict(orient='records')
            elif isinstance(df_result, list):
                data_list = df_result
            else:
                # Se não for DataFrame nem lista, tratar como erro
                logger.error(f"❌ Expected DataFrame or list, got {type(df_result)}: {df_result}")
                return {
                    "final_response": {
                        "type": "text",
                        "content": f"Erro: resultado inesperado do tipo {type(df_result).__name__}",
                        "user_query": user_query
                    }
                }

            logger.info(f"📊 Converted DataFrame to {len(data_list)} records")
            logger.info(f"📊 Sample record keys: {list(data_list[0].keys()) if (isinstance(data_list, list) and len(data_list) > 0) else 'Empty'}")
            return {"retrieved_data": data_list}

        elif code_gen_response.get("type") == "text":
            # ✅ CORREÇÃO: Garantir que texto seja STRING e preservar user_query
            text_output = str(code_gen_response.get("output"))
            logger.info(f"📝 Text response: {len(text_output)} chars - Returning as final_response")

            return {
                "final_response": {
                    "type": "text",
                    "content": text_output,
                    "user_query": user_query
                }
            }

        elif code_gen_response.get("type") == "error":
            error_msg = str(code_gen_response.get("output", "Erro desconhecido"))
            logger.error(f"❌ CodeGenAgent error: {error_msg}")

            return {
                "final_response": {
                    "type": "text",
                    "content": f"❌ Erro ao processar: {error_msg}",
                    "user_query": user_query
                }
            }

        else:
            # ✅ FALLBACK: Tipo desconhecido
            logger.warning(f"⚠️ Unknown CodeGenAgent response type: {code_gen_response.get('type')}")

            return {
                "final_response": {
                    "type": "text",
                    "content": f"⚠️ Resposta inesperada do agente: {code_gen_response.get('output')}",
                    "user_query": user_query
                }
            }

    except Exception as e:
        logger.error(f"Erro ao gerar script Python com CodeGenAgent: {e}", exc_info=True)
        return {"final_response": {"type": "text", "content": f"Não consegui gerar a análise. Erro interno: {e}"}}


def format_final_response(state: AgentState) -> Dict[str, Any]:
    """
    Formata a resposta final para o utilizador.
    """
    user_query = _extract_user_query(state)
    logger.info(f"[NODE] format_final_response: Formatando resposta para '{user_query}'")

    # 🔍 LOGS DETALHADOS DO ESTADO
    logger.info(f"🔍 STATE KEYS: {list(state.keys())}")
    logger.info(f"🔍 clarification_needed: {state.get('clarification_needed')}")
    logger.info(f"🔍 plotly_spec exists: {bool(state.get('plotly_spec'))}")
    logger.info(f"🔍 retrieved_data exists: {bool(state.get('retrieved_data'))}")
    logger.info(f"🔍 final_response exists: {bool(state.get('final_response'))}")

    # Se retrieved_data existir, logar detalhes
    if state.get("retrieved_data"):
        data = state.get("retrieved_data")
        logger.info(f"📊 retrieved_data type: {type(data)}")
        logger.info(f"📊 retrieved_data length: {len(data) if isinstance(data, list) else 'N/A'}")
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            logger.info(f"📊 retrieved_data sample keys: {list(data[0].keys())}")
        elif isinstance(data, list) and len(data) > 0:
            logger.warning(f"⚠️ First item is not dict: {type(data[0])}")

    # 📝 Construir resposta baseada no estado
    response = {}

    # ✅ PRIORIDADE 1: Verificar se já existe final_response (resposta direta do CodeGenAgent)
    if state.get("final_response"):
        logger.info(f"✅ Using pre-formatted final_response from state")
        response = state.get("final_response")
        # Garantir que user_query esteja presente
        if "user_query" not in response:
            response["user_query"] = user_query

    # ✅ PRIORIDADE 2: Clarificação
    elif state.get("clarification_needed"):
        response = {"type": "clarification", "content": state.get("clarification_options")}
        logger.info(f"💬 CLARIFICATION RESPONSE for query: '{user_query}'")

    # ✅ PRIORIDADE 3: Gráfico
    elif state.get("plotly_spec"):
        response = {"type": "chart", "content": state.get("plotly_spec")}
        response["user_query"] = user_query
        logger.info(f"📈 CHART RESPONSE for query: '{user_query}'")

    # ✅ PRIORIDADE 4: Dados tabulares
    elif state.get("retrieved_data"):
        data = state.get("retrieved_data")
        response = {"type": "data", "content": _clean_json_values(data)}
        response["user_query"] = user_query
        logger.info(f"📊 DATA RESPONSE for query: '{user_query}' - {len(data)} rows")

    # ❌ FALLBACK: Se nenhum dos acima
    else:
        response = {
            "type": "text",
            "content": "❌ Não consegui processar a sua solicitação. Tente reformular a pergunta."
        }
        response["user_query"] = user_query
        logger.warning(f"❓ FALLBACK RESPONSE for query: '{user_query}' - No data in state")
        logger.warning(f"❓ State keys available: {list(state.keys())}")

    # ✅ GARANTIR que a pergunta do usuário seja preservada no histórico
    final_messages = state['messages'] + [{"role": "assistant", "content": response}]

    # 🔍 LOG DO RESULTADO FINAL
    logger.info(f"✅ FINAL RESPONSE - Type: {response.get('type')}, User Query: '{user_query}'")
    logger.info(f"📋 MESSAGE HISTORY - Total messages: {len(final_messages)}")

    return {"messages": final_messages, "final_response": response}


def execute_une_tool(state: AgentState) -> Dict[str, Any]:
    """
    Executa ferramentas UNE baseado na query do usuário.
    Detecta qual ferramenta UNE usar e extrai os parâmetros necessários.
    """
    llm_adapter = _factory.get_code_generation_llm() # Ferramentas UNE também são complexas
    if not llm_adapter:
        logger.error("Não foi possível obter o LLM para execução de ferramenta UNE.")
        return {"final_response": {"type": "error", "content": "Erro interno de configuração do LLM."}}
    user_query = _extract_user_query(state)
    logger.info(f"[NODE] execute_une_tool: Processando query UNE '{user_query}'")

    # Importar mapeamento de UNE
    from core.config.une_mapping import resolve_une_code, suggest_une, get_une_name

    # Importar ferramentas UNE
    from core.tools.une_tools import (
        calcular_abastecimento_une,
        calcular_mc_produto,
        calcular_preco_final_une,
        calcular_produtos_sem_vendas
    )

    # 🚀 OTIMIZAÇÃO: Combinar detecção de ferramenta + extração de parâmetros em UMA ÚNICA chamada LLM
    # Isso reduz de 2 chamadas para 1, economizando ~10s por query
    unified_prompt = f"""
    # 🛠️ Analisador de Operações UNE (Otimizado)

    Analise a query do usuário e:
    1. Identifique qual ferramenta UNE usar
    2. Extraia os parâmetros necessários

    ## 📚 EXEMPLOS (Few-Shot Learning)

    **Exemplo 1 - MC:**
    Query: "qual a MC do produto 704559 na une scr?"
    Output: {{"tool": "calcular_mc_produto", "params": {{"produto_id": 704559, "une": "scr"}}, "confidence": 0.98}}

    **Exemplo 2 - MC simplificado:**
    Query: "mc do produto 369947 na une nit"
    Output: {{"tool": "calcular_mc_produto", "params": {{"produto_id": 369947, "une": "nit"}}, "confidence": 0.97}}

    **Exemplo 3 - Abastecimento:**
    Query: "quais produtos precisam abastecimento na UNE MAD?"
    Output: {{"tool": "calcular_abastecimento_une", "params": {{"une_input": "mad", "segmento": null}}, "confidence": 0.95}}

    **Exemplo 4 - Preço:**
    Query: "calcule o preço de R$ 800 ranking 0 a vista"
    Output: {{"tool": "calcular_preco_final_une", "params": {{"valor_compra": 800, "ranking": 0, "forma_pagamento": "vista"}}, "confidence": 0.92}}

    **Exemplo 5 - Estoque (usar MC como proxy):**
    Query: "qual é o estoque do produto 59294 na une scr"
    Output: {{"tool": "calcular_mc_produto", "params": {{"produto_id": 59294, "une": "scr"}}, "confidence": 0.90}}

    **Exemplo 6 - Produtos sem vendas:**
    Query: "quais produtos na une scr estão sem giro"
    Output: {{"tool": "calcular_produtos_sem_vendas", "params": {{"une_input": "scr", "limite": 50}}, "confidence": 0.95}}

    **Exemplo 7 - Produtos sem vendas (variação):**
    Query: "quantos produtos estão sem vendas na une 261"
    Output: {{"tool": "calcular_produtos_sem_vendas", "params": {{"une_input": "261", "limite": 50}}, "confidence": 0.93}}
    
    **Exemplo 8 - Ruptura (mapear para produtos sem vendas):**
    Query: "quais produtos do fabricante kit esta com ruptura na une 261"
    Output: {{"tool": "calcular_produtos_sem_vendas", "params": {{"une_input": "261", "fabricante": "kit", "limite": 50}}, "confidence": 0.98}}


    ## 🎯 FERRAMENTAS DISPONÍVEIS E SEUS PARÂMETROS

    1. **calcular_mc_produto** (Para queries sobre MC, média, estoque de um produto específico)
       - Parâmetros: {{"produto_id": <int>, "une": "<sigla_une>"}}

    2. **calcular_abastecimento_une** (Para queries sobre abastecimento ou reposição)
       - Parâmetros: {{"une_input": "<sigla_une>", "segmento": "<nome_segmento ou null>"}}

    3. **calcular_preco_final_une** (Para queries sobre cálculo de preço, desconto)
       - Parâmetros: {{"valor_compra": <float>, "ranking": <0-4>, "forma_pagamento": "<vista|30d|90d|120d>"}}

    4. **calcular_produtos_sem_vendas** (Para queries sobre produtos sem giro, sem vendas, parados, ou **ruptura**)
       - Parâmetros: {{"une_input": "<sigla_une>", "limite": <int, default 50>, "fabricante": "<nome_fabricante ou null>"}}

    ## 🎯 QUERY ATUAL: "{user_query}"

    ## 📤 RETORNE JSON:
    ```json
    {{
      "tool": "nome_da_ferramenta_escolhida",
      "params": {{...}},
      "confidence": 0.95
    }}
    ```
    """

    # 🔥 NOVO: Passar contexto ao cache para separar operações UNE
    cache_context = {"operation": "une_tool", "query_type": "une_operation"}
    tool_response = llm_adapter.get_completion(
        messages=[{"role": "user", "content": unified_prompt}],
        json_mode=True,
        cache_context=cache_context
    )

    tool_str = tool_response.get("content", "{}").strip()
    if "```json" in tool_str:
        match = re.search(r"```json\n(.*?)```", tool_str, re.DOTALL)
        if match:
            tool_str = match.group(1).strip()

    try:
        tool_data = json.loads(tool_str)
        tool_name = tool_data.get("tool", "")
        confidence = tool_data.get("confidence", 0.5)
        params = tool_data.get("params", {})  # 🚀 NOVO: Parâmetros já vêm extraídos!
    except json.JSONDecodeError:
        logger.error(f"Erro ao parsear resposta UNE: {tool_str}")
        return {"final_response": {"type": "text", "content": "Não consegui identificar a operação UNE solicitada."}}

    logger.info(f"🔧 Ferramenta UNE: {tool_name} (confidence: {confidence:.2f})")
    logger.info(f"📦 Parâmetros extraídos: {params}")

    # Validar confidence mínimo
    if confidence < 0.6:
        logger.warning(f"⚠️ Baixa confiança na detecção de ferramenta UNE: {confidence:.2f}")
        # Continuar mesmo assim, mas logar aviso

    # Executar ferramenta apropriada
    try:
        if "abastecimento" in tool_name:
            # 🚀 OTIMIZADO: Parâmetros já foram extraídos na chamada unificada!
            une_input = params.get("une_input", "")
            segmento = params.get("segmento")

            # ✅ VALIDAR E RESOLVER UNE usando mapeamento
            une_code = resolve_une_code(une_input)

            if not une_code:
                # UNE não encontrada - sugerir alternativas
                suggestions = suggest_une(une_input)
                if suggestions:
                    sugg_text = ", ".join([f"{code} ({name})" for code, name in suggestions])
                    error_msg = f"❌ UNE '{une_input}' não encontrada.\n\n💡 Você quis dizer: {sugg_text}?"
                else:
                    error_msg = f"❌ UNE '{une_input}' não encontrada.\n\nUNEs disponíveis: SCR (123), MAD (261), UNA (301), VIX (401), JFA (501), BHE (601)"

                logger.warning(f"UNE não encontrada: '{une_input}'")
                return {"final_response": {"type": "text", "content": error_msg, "user_query": user_query}}

            # Converter une_code para int de forma segura
            try:
                une_id = int(une_code)
            except (ValueError, TypeError) as e:
                logger.error(f"❌ Erro ao converter UNE code '{une_code}' para int: {e}")
                return {
                    "final_response": {
                        "type": "text",
                        "content": f"❌ Erro ao processar UNE '{une_input}'. O código '{une_code}' não é válido.",
                        "user_query": user_query
                    }
                }

            une_name = get_une_name(une_code)
            logger.info(f"✅ UNE resolvida: '{une_input}' → {une_code} ({une_name})")

            args = {"une_id": une_id}
            if segmento:
                args["segmento"] = segmento

            result = calcular_abastecimento_une.invoke(args)

        elif "mc_produto" in tool_name:
            # 🚀 OTIMIZADO: Parâmetros já foram extraídos na chamada unificada!
            produto_id_str = params.get("produto_id")
            une_input = params.get("une")

            # ✅ VALIDAÇÃO: Verificar se parâmetros foram extraídos
            if produto_id_str is None or produto_id_str == "":
                logger.error(f"❌ produto_id não foi extraído dos parâmetros. Params: {params}")
                logger.error(f"❌ Query original: {user_query}")

                # Tentar extrair produto_id diretamente da query como fallback
                import re
                match = re.search(r'\b(\d{5,})\b', user_query)
                if match:
                    produto_id_str = match.group(1)
                    logger.info(f"✅ Produto_id extraído da query via regex: {produto_id_str}")
                else:
                    return {
                        "final_response": {
                            "type": "text",
                            "content": f"❌ Não consegui identificar o código do produto na consulta.\n\nPor favor, informe o código do produto (ex: 'MC do produto 369947 na UNE SCR')",
                            "user_query": user_query
                        }
                    }

            if une_input is None or une_input == "":
                logger.error(f"❌ UNE não foi extraída dos parâmetros. Params: {params}")
                return {
                    "final_response": {
                        "type": "text",
                        "content": f"❌ Não consegui identificar a UNE na consulta.\n\nPor favor, informe a UNE (ex: 'MC do produto 369947 na UNE SCR')",
                        "user_query": user_query
                    }
                }

            # Converter produto_id com segurança
            try:
                produto_id = int(produto_id_str)
            except (ValueError, TypeError) as e:
                logger.error(f"❌ Erro ao converter produto_id '{produto_id_str}' para int: {e}")
                return {
                    "final_response": {
                        "type": "text",
                        "content": f"❌ Erro ao processar o código do produto '{produto_id_str}'.\n\nO código deve ser um número válido.",
                        "user_query": user_query
                    }
                }

            # Resolver UNE usando mapeamento
            une_code = resolve_une_code(une_input)
            if not une_code:
                # Tentar sugestões
                suggestions = suggest_une(une_input)
                if suggestions:
                    sugg_text = ", ".join([f"{code} ({name})" for code, name in suggestions])
                    error_msg = f"❌ UNE '{une_input}' não encontrada.\n\n💡 Você quis dizer: {sugg_text}?"
                else:
                    error_msg = f"❌ UNE '{une_input}' não encontrada.\n\nUNEs disponíveis: SCR (1), MAD (2720), BAR (2365), etc."

                logger.warning(f"UNE não encontrada para MC: '{une_input}'")
                return {"final_response": {"type": "text", "content": error_msg, "user_query": user_query}}

            # Converter une_code para int
            try:
                une_id = int(une_code)
            except (ValueError, TypeError) as e:
                logger.error(f"❌ Erro ao converter UNE code '{une_code}' para int: {e}")
                return {
                    "final_response": {
                        "type": "text",
                        "content": f"❌ Erro ao processar UNE '{une_input}'. O código '{une_code}' não é válido.",
                        "user_query": user_query
                    }
                }

            logger.info(f"✅ Parâmetros MC extraídos: produto_id={produto_id}, une={une_input}→{une_id}")
            result = calcular_mc_produto.invoke({"produto_id": produto_id, "une_id": une_id})

        elif "preco" in tool_name:
            # 🚀 OTIMIZADO: Parâmetros já foram extraídos na chamada unificada!
            # Converter parâmetros com segurança
            try:
                valor_compra = float(params.get("valor_compra"))
                ranking = int(params.get("ranking"))
                forma_pagamento = params.get("forma_pagamento")
            except (ValueError, TypeError) as e:
                logger.error(f"❌ Erro ao converter parâmetros de preço: {e}")
                logger.error(f"Parâmetros recebidos: {params}")
                return {
                    "final_response": {
                        "type": "text",
                        "content": f"❌ Erro ao processar parâmetros de preço. Verifique os valores informados.",
                        "user_query": user_query
                    }
                }

            result = calcular_preco_final_une.invoke({
                "valor_compra": valor_compra,
                "ranking": ranking,
                "forma_pagamento": forma_pagamento
            })

        elif "sem_vendas" in tool_name or "sem giro" in user_query.lower():
            # 🚀 NOVA FERRAMENTA: Produtos sem vendas
            une_input = params.get("une_input", "")
            limite = params.get("limite", 50)

            # Validar e resolver UNE
            une_code = resolve_une_code(une_input)

            if not une_code:
                suggestions = suggest_une(une_input)
                if suggestions:
                    sugg_text = ", ".join([f"{code} ({name})" for code, name in suggestions])
                    error_msg = f"❌ UNE '{une_input}' não encontrada.\n\n💡 Você quis dizer: {sugg_text}?"
                else:
                    error_msg = f"❌ UNE '{une_input}' não encontrada.\n\nUNEs disponíveis: SCR (2586), MAD (261), UNA (301), VIX (401), etc."

                logger.warning(f"UNE não encontrada: '{une_input}'")
                return {"final_response": {"type": "text", "content": error_msg, "user_query": user_query}}

            # Converter une_code para int
            try:
                une_id = int(une_code)
            except (ValueError, TypeError) as e:
                logger.error(f"❌ Erro ao converter UNE code '{une_code}' para int: {e}")
                return {
                    "final_response": {
                        "type": "text",
                        "content": f"❌ Erro ao processar UNE '{une_input}'. O código '{une_code}' não é válido.",
                        "user_query": user_query
                    }
                }

            une_name = get_une_name(une_code)
            logger.info(f"✅ UNE resolvida: '{une_input}' → {une_code} ({une_name})")

            result = calcular_produtos_sem_vendas.invoke({"une_id": une_id, "limite": limite})

        else:
            return {"final_response": {"type": "text", "content": f"Ferramenta UNE '{tool_name}' não reconhecida."}}

        # Verificar se houve erro
        if "error" in result:
            return {"final_response": {"type": "text", "content": f"Erro: {result['error']}"}}

        # Formatar resposta baseado no tipo de ferramenta
        if "produtos" in result and "criterio" in result:  # Produtos sem vendas
            # ✅ NOVO: Formatar produtos sem vendas + dados para download
            response_text = format_produtos_sem_vendas_response(result)

            # Retornar resposta formatada + dados brutos para download
            return {
                "final_response": {
                    "type": "text_with_data",
                    "content": response_text,
                    "download_data": result.get("produtos", []),
                    "download_filename": f"produtos_sem_vendas_une_{result.get('une_id', 'unknown')}",
                    "user_query": user_query
                }
            }
        elif "produtos" in result:  # Abastecimento
            # ✅ NOVO: Usar formatação ideal para lista de abastecimento
            total_produtos = result.get('total_produtos', 0)
            if total_produtos == 0:
                # Se não há produtos, retornar texto formatado
                response_text = format_abastecimento_response(result)
                return {"final_response": {"type": "text", "content": response_text}}
            elif total_produtos <= 10:
                # Se poucos produtos, mostrar como texto formatado + download
                response_text = format_abastecimento_response(result)
                return {
                    "final_response": {
                        "type": "text_with_data",
                        "content": response_text,
                        "download_data": result.get("produtos", []),
                        "download_filename": f"abastecimento_une_{result.get('une_id', 'unknown')}",
                        "user_query": user_query
                    }
                }
            else:
                # Se muitos produtos, retornar como tabela (formato original)
                # Mas adicionar cabeçalho formatado antes
                header = f"Produtos que Precisam Abastecimento - UNE {result['une_id']} ({result.get('segmento', 'Todos')})\nTotal: {total_produtos} produtos\n\n"
                return {"retrieved_data": result.get("produtos", []), "summary": header}
        elif "mc_calculada" in result:  # MC - Formatar para usuário
            response_text = format_mc_response(result)
            return {"final_response": {"type": "text", "content": response_text}}
        elif "valor_original" in result:  # Preço - Formatar para usuário
            response_text = format_preco_response(result)
            return {"final_response": {"type": "text", "content": response_text}}
        else:  # Fallback - JSON formatado
            response_text = json.dumps(result, indent=2, ensure_ascii=False)
            return {"final_response": {"type": "text", "content": response_text}}

    except Exception as e:
        logger.error(f"Erro ao executar ferramenta UNE: {e}", exc_info=True)
        return {"final_response": {"type": "text", "content": f"Erro ao processar operação UNE: {str(e)}"}}


def generate_initial_feedback(state: AgentState) -> dict:
    """
    🎯 MELHORIA: Gera feedback inicial para o usuário antes do processamento analítico.

    Esta função informa ao usuário o que o agente irá fazer, melhorando a transparência
    e experiência do usuário ao deixar claro que a solicitação foi compreendida e está
    sendo processada.

    Args:
        state: Estado atual do agente com reasoning_result

    Returns:
        Dict vazio (não modifica o estado, apenas registra a ação planejada)
    """
    reasoning_result = state.get("reasoning_result", {})
    messages = state.get("messages", [])

    # Extrair informações do reasoning
    reasoning = reasoning_result.get("reasoning", "")
    emotional_tone = reasoning_result.get("emotional_tone", "neutro")

    # Extrair a query do usuário
    user_query = ""
    if messages:
        last_msg = messages[-1]
        user_query = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)

    # Gerar mensagem de feedback baseada no raciocínio
    feedback_message = _create_feedback_message(user_query, reasoning, emotional_tone)

    # Armazenar no estado para ser exibida antes do processamento
    logger.info(f"💬 Feedback inicial gerado: {feedback_message[:100]}...")

    return {
        "initial_feedback": feedback_message
    }


def _create_feedback_message(query: str, reasoning: str, tone: str) -> str:
    """
    Cria uma mensagem de feedback inicial natural e contextualizada.

    Args:
        query: Query do usuário
        reasoning: Raciocínio do agente
        tone: Tom emocional detectado

    Returns:
        Mensagem de feedback formatada
    """
    # Detectar tipo de análise baseado na query
    query_lower = query.lower()

    # Análise de vendas
    if any(keyword in query_lower for keyword in ["vendas", "venda", "faturamento", "receita"]):
        if "oxford" in query_lower or "tecido" in query_lower:
            action = "analisar as vendas dos tecidos oxford"
        else:
            action = "analisar os dados de vendas"

    # Análise de MC
    elif "mc" in query_lower or "média comum" in query_lower:
        action = "calcular a Média Comum (MC)"

    # Análise de estoque
    elif "estoque" in query_lower:
        action = "verificar os dados de estoque"

    # Análise de abastecimento
    elif "abastec" in query_lower:
        action = "calcular o abastecimento necessário"

    # Gráfico/visualização
    elif "gráfico" in query_lower or "grafico" in query_lower or "chart" in query_lower:
        action = "gerar o gráfico solicitado"

    # Produtos sem vendas
    elif "sem vendas" in query_lower or "sem giro" in query_lower:
        action = "identificar produtos sem vendas"

    # Análise de segmento
    elif "segmento" in query_lower:
        action = "analisar os dados do segmento"

    # Análise genérica
    else:
        action = "processar sua solicitação"

    # Adaptar mensagem ao tom emocional
    if tone == "urgente":
        prefix = "Entendi! Vou"
        suffix = "rapidinho para você. Aguarde um momento..."
    elif tone == "frustrado":
        prefix = "Sem problemas! Deixa comigo, vou"
        suffix = "agora. Só um instante..."
    elif tone == "curioso":
        prefix = "Boa pergunta! Vou"
        suffix = "para te mostrar. Aguarde..."
    elif tone == "casual":
        prefix = "Beleza! Vou"
        suffix = "para você. Um momento..."
    else:  # neutro ou confuso
        prefix = "Certo! Vou"
        suffix = "agora. Aguarde um momento..."

    return f"{prefix} {action} {suffix}"