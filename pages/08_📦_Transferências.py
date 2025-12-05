"""
Página de Transferências entre UNEs
Permite solicitar transferências de produtos entre lojas/depósitos
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import json
import io

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuração da página
st.set_page_config(
    page_title="Transferências entre UNEs",
    page_icon="📦",
    layout="wide"
)

# Verificar autenticação
if not st.session_state.get("authenticated"):
    st.warning("⚠️ Por favor, faça login na página principal")
    st.stop()

# Importar backend
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.tools.une_tools import validar_transferencia_produto, sugerir_transferencias_automaticas

# Instanciar o adapter localmente. Não armazenar no session_state.
adapter = HybridDataAdapter()

# Título
st.title("📦 Transferências entre UNEs")
st.markdown("Solicite transferências de produtos entre lojas e depósito central")

# --- FUNÇÃO: Carregar UNEs disponíveis ---
@st.cache_data(ttl=300)
def get_unes_disponiveis():
    """Retorna lista de UNEs disponíveis, filtradas pelo segmento do usuário"""
    user_segmento = st.session_state.get("segmento")
    user_role = st.session_state.get("role") # Get user role

    try:
        # Carregar dados com filtro mínimo (apenas colunas necessárias)
        # Como não podemos filtrar sem critérios, vamos usar a fonte diretamente
        import os
        from pathlib import Path

        # Tentar carregar do Parquet diretamente
        parquet_path = Path(__file__).parent.parent / 'data' / 'parquet'

        # Usar arquivo correto (admmat.parquet)
        parquet_file = parquet_path / 'admmat.parquet'
        
        if not parquet_file.exists():
            st.error(f"❌ Arquivo Parquet não encontrado em {parquet_file}")
            return []

        # Carregar apenas colunas UNE e nomesegmento
        df = pd.read_parquet(parquet_file, columns=['une', 'une_nome', 'nomesegmento'])
        
        # Lógica de filtragem de segmento aprimorada
        # Se o segmento do usuário não estiver definido OU o usuário for admin, não aplicar filtro de segmento
        if not user_segmento or user_role == "admin":
            df_filtered = df # Não aplicar filtro de segmento
        else:
            # Filtrar por segmento do usuário
            df_filtered = df[df['nomesegmento'] == user_segmento]
        
        unes = df_filtered[['une', 'une_nome']].drop_duplicates().sort_values('une')
        return unes.to_dict('records')
    except Exception as e:
        st.error(f"Erro ao carregar UNEs: {e}")
        import traceback
        st.error(traceback.format_exc())
    return []

# --- FUNÇÃO: Carregar produtos da UNE (OTIMIZADO) ---
@st.cache_data(ttl=300, show_spinner=False)
def get_produtos_une(une_id):
    """
    Carrega produtos com estoque da UNE (OTIMIZADO com PyArrow + cache)
    Cache de 5 minutos para evitar recarregamentos desnecessários
    Performance esperada: <0.5s para 1000 produtos
    """
    import time
    start_time = time.time()

    user_segmento = st.session_state.get("segmento")
    user_role = st.session_state.get("role") # Get user role

    segment_filter_active = True # Default to active

    if user_role == "admin":
        st.info("✅ Admin logado: filtro de segmento desativado para produtos da UNE.")
        segment_filter_active = False
    elif not user_segmento:
        st.error("❌ Segmento do usuário não definido. Faça login novamente.")
        return []

    try:
        import pyarrow.parquet as pq
        import pyarrow.compute as pc

        parquet_file = Path(__file__).parent.parent / 'data' / 'parquet' / 'admmat.parquet'
        
        if not parquet_file.exists():
            st.error(f"❌ Arquivo Parquet não encontrado em {parquet_file}")
            return []

        # OTIMIZAÇÃO: PyArrow com push-down filters
        filters_list = [('une', '=', int(une_id))]
        if segment_filter_active:
            filters_list.append(('nomesegmento', '=', user_segmento))

        table = pq.read_table(
            parquet_file,
            columns=['codigo', 'nome_produto', 'estoque_atual', 'venda_30_d', 'preco_38_percent', 'nomesegmento', 'NOMEFABRICANTE'],
            filters=filters_list
        )

        # Converter para pandas
        df = table.to_pandas()

        # Converter estoque para numérico
        df['estoque_atual'] = pd.to_numeric(df['estoque_atual'], errors='coerce').fillna(0)

        # Filtrar apenas produtos com estoque
        df = df[df['estoque_atual'] > 0]

        # Limitar a 1000 produtos mais relevantes (ordenar por venda ou estoque)
        if 'venda_30_d' in df.columns:
            df['venda_30_d'] = pd.to_numeric(df['venda_30_d'], errors='coerce').fillna(0)
            df = df.nlargest(1000, 'venda_30_d')  # Top 1000 por vendas
        else:
            df = df.nlargest(1000, 'estoque_atual')  # Top 1000 por estoque

        elapsed = time.time() - start_time
        result = df.to_dict('records') if len(df) > 0 else []

        # Log de performance (apenas em debug)
        if elapsed > 2.0:  # Se demorar mais de 2s, alertar
            st.warning(f"⚠️ Carregamento da UNE {une_id} demorou {elapsed:.2f}s (esperado <0.5s)")

        return result

    except ImportError:
        # Fallback se PyArrow não estiver disponível
        st.warning("⚠️ PyArrow não disponível - performance reduzida")
        parquet_file = Path(__file__).parent.parent / 'data' / 'parquet' / 'admmat.parquet'

        df = pd.read_parquet(parquet_file)
        df = df[df['une'] == int(une_id)]
        
        if segment_filter_active:
            df = df[df['nomesegmento'] == user_segmento] # Add segment filter here too

        df['estoque_atual'] = pd.to_numeric(df['estoque_atual'], errors='coerce').fillna(0)
        df = df[df['estoque_atual'] > 0].head(1000)

        elapsed = time.time() - start_time
        if elapsed > 5.0:
            st.warning(f"⚠️ Carregamento lento: {elapsed:.2f}s. Instale PyArrow para melhor performance.")

        return df.to_dict('records') if len(df) > 0 else []

    except Exception as e:
        st.error(f"❌ Erro ao carregar produtos da UNE {une_id}: {str(e)[:150]}")
        # Não mostrar traceback completo para não assustar usuário
        with st.expander("🔍 Detalhes técnicos do erro"):
            import traceback
            st.code(traceback.format_exc())
        return []

# --- SIDEBAR: Configuração da Transferência ---
st.sidebar.header("🔧 Configuração")

# Carregar UNEs
unes = get_unes_disponiveis()

if not unes:
    st.error("❌ Nenhuma UNE encontrada. Verifique a conexão com o banco de dados.")
    st.stop()

# Criar dicionário UNE -> Nome
une_map = {u['une']: f"UNE {u['une']} - {u['une_nome']}" for u in unes}
une_ids = list(une_map.keys())

# MODO DE TRANSFERÊNCIA
st.sidebar.subheader("🔀 Modo de Transferência")
modo_transferencia = st.sidebar.radio(
    "Selecione o modo",
    ["1 → 1 (Uma origem, um destino)",
     "1 → N (Uma origem, múltiplos destinos)",
     "N → N (Múltiplas origens, múltiplos destinos)"],
    key='modo_transferencia'
)

st.sidebar.markdown("---")

# Seleção de UNE(s) Origem
st.sidebar.subheader("📍 Origem")

if "N → N" in modo_transferencia:
    # Modo N→N: múltiplas origens
    unes_origem = st.sidebar.multiselect(
        "Selecione UNEs de origem",
        une_ids,
        format_func=lambda x: une_map[x],
        key='unes_origem_multi'
    )
    if not unes_origem:
        st.sidebar.warning("⚠️ Selecione pelo menos uma UNE de origem")
else:
    # Modo 1→1 ou 1→N: uma origem
    une_origem_single = st.sidebar.selectbox(
        "Selecione a UNE de origem",
        une_ids,
        format_func=lambda x: une_map[x],
        key='une_origem_single'
    )
    unes_origem = [une_origem_single]

# Seleção de UNE(s) Destino
st.sidebar.subheader("📍 Destino")

if "1 → 1" in modo_transferencia:
    # Modo 1→1: um destino
    unes_destino_disponiveis = [u for u in une_ids if u not in unes_origem]
    if unes_destino_disponiveis:
        une_destino_single = st.sidebar.selectbox(
            "Selecione a UNE de destino",
            unes_destino_disponiveis,
            format_func=lambda x: une_map[x],
            key='une_destino_single'
        )
        unes_destino = [une_destino_single]
    else:
        st.sidebar.error("❌ Nenhuma UNE disponível para destino")
        unes_destino = []
else:
    # Modo 1→N ou N→N: múltiplos destinos
    unes_destino_disponiveis = [u for u in une_ids if u not in unes_origem]
    unes_destino = st.sidebar.multiselect(
        "Selecione UNEs de destino",
        unes_destino_disponiveis,
        format_func=lambda x: une_map[x],
        key='unes_destino_multi'
    )
    if not unes_destino:
        st.sidebar.warning("⚠️ Selecione pelo menos uma UNE de destino")

st.sidebar.markdown("---")

# Informações da transferência
if unes_origem and unes_destino:
    origem_str = ", ".join([f"UNE {u}" for u in unes_origem])
    destino_str = ", ".join([f"UNE {u}" for u in unes_destino])

    st.sidebar.info(f"""
**Transferência:**
- **Modo:** {modo_transferencia.split(' ')[0]}
- **Origem:** {origem_str}
- **Destino:** {destino_str}
""")
else:
    st.sidebar.warning("⚠️ Configure origem e destino")

# Validar configuração
if not unes_origem or not unes_destino:
    st.warning("⚠️ Configure origem e destino na barra lateral")
    st.stop()

# --- ÁREA PRINCIPAL: Seleção de Produtos ---
if "N → N" in modo_transferencia:
    st.subheader(f"🔍 Produtos disponíveis - {len(unes_origem)} UNEs de origem")
else:
    st.subheader(f"🔍 Produtos disponíveis na UNE {unes_origem[0]}")

# Carregar produtos de todas as UNEs de origem (COM PROGRESS BAR)
produtos_por_une = {}

# Progress bar para melhor UX
if len(unes_origem) > 1:
    progress_text = st.empty()
    progress_bar = st.progress(0)

    for idx, une in enumerate(unes_origem):
        progress_text.text(f"🔄 Carregando UNE {une}... ({idx+1}/{len(unes_origem)})")
        progress_bar.progress((idx + 1) / len(unes_origem))

        prods = get_produtos_une(une)
        if prods:
            produtos_por_une[une] = prods

    progress_text.empty()
    progress_bar.empty()
else:
    # Uma única UNE: spinner simples
    with st.spinner(f"Carregando produtos da UNE {unes_origem[0]}..."):
        prods = get_produtos_une(unes_origem[0])
        if prods:
            produtos_por_une[unes_origem[0]] = prods

if not produtos_por_une:
    st.warning(f"⚠️ Nenhum produto com estoque encontrado nas UNEs selecionadas")
    st.info("💡 **Dica:** Tente selecionar outras UNEs ou verifique se há produtos com estoque disponível.")
    st.stop()

# Combinar produtos de todas as origens
produtos_todos = []
for une, prods in produtos_por_une.items():
    for p in prods:
        p['une_origem'] = une  # Adicionar UNE de origem
        produtos_todos.append(p)

produtos = produtos_todos

# Filtros
col1, col2, col3, col4 = st.columns(4)

with col1:
    busca = st.text_input("🔎 Buscar (ex: tnt, 25., 123)", "",
                          help="Digite código/nome. Use ponto final (25.) para busca exata")

with col2:
    user_segmento = st.session_state.get("segmento")
    user_role = st.session_state.get("role")
    segmentos_disponiveis = list(set([p.get('nomesegmento', 'N/A') for p in produtos if p.get('nomesegmento')]))
    
    # Admin sempre tem acesso a todos os segmentos (não desabilitado)
    # Usuários normais com segmento definido só veem seu segmento (desabilitado)
    if user_role == "admin":
        # Admin vê todos os segmentos e pode mudar
        segmento_filtro_options = ["Todos"] + sorted(segmentos_disponiveis)
        default_segmento_index = 0
        is_segmento_disabled = False
        st.markdown("✅ **Admin:** Acesso a todos os segmentos")
    elif user_segmento and user_segmento != "Todos":
        # Usuário normal vê apenas seu segmento
        segmento_filtro_options = [user_segmento]
        default_segmento_index = 0
        is_segmento_disabled = True
    else:
        # Sem segmento definido
        segmento_filtro_options = ["Todos"] + sorted(segmentos_disponiveis)
        default_segmento_index = 0
        is_segmento_disabled = False

    segmento_filtro = st.selectbox(
        "Segmento",
        segmento_filtro_options,
        index=default_segmento_index,
        disabled=is_segmento_disabled
    )

with col3:
    # FILTRO DINÂMICO: Fabricantes filtrados pelo segmento selecionado
    if segmento_filtro != "Todos":
        # Filtrar produtos do segmento selecionado
        produtos_segmento = [p for p in produtos if p.get('nomesegmento') == segmento_filtro]
        # Extrair fabricantes apenas desses produtos
        fabricantes = list(set([p.get('NOMEFABRICANTE', 'N/A') for p in produtos_segmento if p.get('NOMEFABRICANTE')]))
    else:
        # Se "Todos" segmentos, mostra todos fabricantes
        fabricantes = list(set([p.get('NOMEFABRICANTE', 'N/A') for p in produtos if p.get('NOMEFABRICANTE')]))

    fabricante_filtro = st.selectbox("Fabricante", ["Todos"] + sorted(fabricantes))

with col4:
    min_estoque = st.number_input("Estoque mín.", min_value=0, value=0)

# Aplicar filtros
produtos_filtrados = produtos.copy()

if busca:
    busca_norm = busca.strip().replace('%', '')

    # Busca exata se terminar com ponto
    if busca_norm.endswith('.'):
        busca_exata = busca_norm[:-1]  # Remove o ponto
        produtos_filtrados = [
            p for p in produtos_filtrados
            if str(p.get('codigo', '')).replace('.0', '').strip() == busca_exata
            or p.get('nome_produto', '').strip().lower() == busca_exata.lower()
        ]
    else:
        # Busca parcial
        produtos_filtrados = [
            p for p in produtos_filtrados
            if busca_norm.lower() in str(p.get('codigo', '')).replace('.0', '').strip().lower()
            or busca_norm.lower() in str(p.get('nome_produto', '')).strip().lower()
        ]

# Always filter by user's segment if available, overriding "Todos"
if user_segmento and user_segmento != "Todos":
    produtos_filtrados = [p for p in produtos_filtrados if p.get('nomesegmento') == user_segmento]
elif segmento_filtro != "Todos": # Only apply if user_segmento is not set or is "Todos"
    produtos_filtrados = [p for p in produtos_filtrados if p.get('nomesegmento') == segmento_filtro]

if fabricante_filtro != "Todos":
    produtos_filtrados = [p for p in produtos_filtrados if p.get('NOMEFABRICANTE') == fabricante_filtro]

if min_estoque > 0:
    produtos_filtrados = [p for p in produtos_filtrados if p.get('estoque_atual', 0) >= min_estoque]

st.info(f"📊 **{len(produtos_filtrados)}** produtos encontrados (de {len(produtos)} total)")

# --- TABELA DE SELEÇÃO ---
if produtos_filtrados:
    st.markdown("### ✅ Selecione os produtos para transferir")

    # Inicializar carrinho e seleções se não existirem
    if 'carrinho_transferencia' not in st.session_state:
        st.session_state.carrinho_transferencia = {}
    if 'produtos_selecionados' not in st.session_state:
        st.session_state.produtos_selecionados = {}

    # Mostrar produtos
    df_produtos = pd.DataFrame(produtos_filtrados)

    # Formatação de preço
    if 'preco_38_percent' in df_produtos.columns:
        df_produtos['preco_38_percent'] = pd.to_numeric(df_produtos['preco_38_percent'], errors='coerce')
        df_produtos['preco_38_percent'] = df_produtos['preco_38_percent'].apply(
            lambda x: f"R$ {x:.2f}" if pd.notna(x) else "N/A"
        )

    # Exibir tabela (paginação manual)
    items_per_page = 10
    total_pages = (len(df_produtos) - 1) // items_per_page + 1

    page = st.number_input("Página", min_value=1, max_value=total_pages, value=1, step=1)

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    df_page = df_produtos.iloc[start_idx:end_idx]

    # Colunas a exibir (incluir une_origem se houver múltiplas origens)
    cols_display = ['codigo', 'nome_produto', 'estoque_atual', 'venda_30_d', 'preco_38_percent', 'nomesegmento', 'NOMEFABRICANTE']
    if 'une_origem' in df_page.columns and len(unes_origem) > 1:
        cols_display.insert(0, 'une_origem')

    st.dataframe(
        df_page[[c for c in cols_display if c in df_page.columns]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown(f"Mostrando {start_idx+1}-{min(end_idx, len(df_produtos))} de {len(df_produtos)} produtos")
    
    # Botões de seleção em massa
    col_sel1, col_sel2, col_sel3 = st.columns([1, 1, 2])
    
    with col_sel1:
        if st.button("✅ Selecionar Tudo", use_container_width=True):
            for idx, row in df_produtos.iterrows():
                codigo = str(row.get('codigo', ''))
                st.session_state.produtos_selecionados[codigo] = True
            st.success(f"✅ {len(df_produtos)} produtos selecionados!")
            st.rerun()
    
    with col_sel2:
        if st.button("❌ Deselecionar Tudo", use_container_width=True):
            st.session_state.produtos_selecionados = {}
            st.info("❌ Todos os produtos deselecioandos")
            st.rerun()
    
    with col_sel3:
        num_selecionados = len([k for k, v in st.session_state.produtos_selecionados.items() if v])
        st.markdown(f"📦 **Selecionados:** {num_selecionados}/{len(df_produtos)} produtos")
    
    # Divisor
    st.markdown("---")
    
    # Exibir checkboxes para cada produto
    st.markdown("**🔍 Clique no checkbox para selecionar o produto:**")
    
    for idx, row in df_page.iterrows():
        codigo = str(row.get('codigo', ''))
        nome = row.get('nome_produto', 'N/A')
        estoque = int(row.get('estoque_atual', 0))
        preco_str = row.get('preco_38_percent', 'N/A')
        
        # Checkbox com informações do produto
        is_selected = st.session_state.produtos_selecionados.get(codigo, False)
        
        col_check, col_info, col_qty = st.columns([0.4, 2, 0.6])
        
        with col_check:
            is_selected = st.checkbox(
                label="",
                value=is_selected,
                key=f"select_{codigo}_{idx}"
            )
            st.session_state.produtos_selecionados[codigo] = is_selected
        
        with col_info:
            status = "✅" if is_selected else "⚪"
            st.write(f"{status} **{codigo}** - {nome} | Estoque: {estoque} | {preco_str}")
        
        with col_qty:
            if is_selected:
                qtd = st.number_input(
                    "Qtd",
                    min_value=1,
                    max_value=estoque if estoque > 0 else 1,
                    value=1,
                    key=f"qty_{codigo}_{idx}"
                )
                st.session_state.produtos_selecionados[f"{codigo}_qtd"] = qtd

    # Botão para adicionar todos os produtos selecionados ao carrinho
    st.markdown("---")
    
    # Contar selecionados
    produtos_selecionados_lista = [
        (codigo, st.session_state.produtos_selecionados.get(f"{codigo}_qtd", 1))
        for codigo in st.session_state.produtos_selecionados.keys()
        if codigo in [str(p.get('codigo', '')) for p in produtos_filtrados] 
        and st.session_state.produtos_selecionados.get(codigo, False)
    ]
    
    if produtos_selecionados_lista:
        col_btn1, col_btn2 = st.columns([2, 1])
        
        with col_btn1:
            st.info(f"📦 **{len(produtos_selecionados_lista)} produto(s) selecionado(s)** - Clique em 'Adicionar ao Carrinho' para prosseguir")
        
        with col_btn2:
            if st.button("🛒 Adicionar ao Carrinho", use_container_width=True, type="primary"):
                # Adicionar cada produto selecionado
                for codigo, qtd in produtos_selecionados_lista:
                    produto = next((p for p in produtos_filtrados if str(p.get('codigo')) == str(codigo)), None)
                    if produto:
                        une_origem = produto.get('une_origem', unes_origem[0])
                        chave = f"{codigo}_UNE{une_origem}"
                        
                        if len(unes_destino) > 1:
                            # Modo N→N: distribuição por destino (distribuir igualmente)
                            qtd_por_destino = int(qtd / len(unes_destino))
                            distribuicao = {une: qtd_por_destino for une in unes_destino}
                            distribuicao[unes_destino[0]] += qtd % len(unes_destino)  # Resto vai para primeiro destino
                        else:
                            # Modo 1→1: transferência para uma UNE
                            distribuicao = {unes_destino[0]: qtd}
                        
                        st.session_state.carrinho_transferencia[chave] = {
                            'produto': produto,
                            'une_origem': une_origem,
                            'distribuicao': distribuicao,
                            'total': qtd,
                            'preco': produto.get('preco_38_percent', 0),
                            'valor_total_item': qtd * pd.to_numeric(produto.get('preco_38_percent', 0), errors='coerce')
                        }
                
                st.success(f"✅ {len(produtos_selecionados_lista)} produto(s) adicionado(s) ao carrinho!")
                st.session_state.produtos_selecionados = {}  # Limpar seleção
                st.rerun()
    else:
        st.info("👇 Selecione os produtos acima para adicionar ao carrinho")

    # Modo 1→N ou N→N: permitir distribuição de quantidade por destino
    if len(unes_destino) > 1:
        st.info(f"💡 **Modo distribuição:** Defina quantidades para cada UNE de destino")

        codigo_add = st.text_input("Código do produto", key='codigo_add_multi')

        if codigo_add:
            # Verificar se produto existe
            produto = next((p for p in produtos_filtrados if str(p.get('codigo')) == str(codigo_add)), None)

            if produto:
                estoque_total = produto.get('estoque_atual', 0)
                une_origem_prod = produto.get('une_origem', unes_origem[0])

                st.write(f"**Produto:** {produto.get('nome_produto')} | **Estoque UNE {une_origem_prod}:** {estoque_total}")

                # Input de quantidade por destino
                st.write("**Distribuição por destino:**")
                distribuicao = {}
                total_distribuido = 0

                cols = st.columns(min(len(unes_destino), 4))
                for idx, une_dest in enumerate(unes_destino):
                    with cols[idx % 4]:
                        qtd = st.number_input(
                            f"UNE {une_dest}",
                            min_value=0,
                            value=0,
                            key=f'dist_{codigo_add}_{une_dest}'
                        )
                        distribuicao[une_dest] = qtd
                        total_distribuido += qtd

                st.write(f"**Total:** {total_distribuido} / {estoque_total}")

                if st.button("➕ Adicionar com distribuição", use_container_width=True):
                    if total_distribuido > estoque_total:
                        st.error(f"❌ Total distribuído ({total_distribuido}) > estoque ({estoque_total})")
                    elif total_distribuido == 0:
                        st.warning("⚠️ Defina pelo menos uma quantidade")
                    else:
                        # Criar chave única: codigo_une_origem
                        chave = f"{codigo_add}_UNE{une_origem_prod}"
                        st.session_state.carrinho_transferencia[chave] = {
                            'produto': produto,
                            'une_origem': une_origem_prod,
                            'distribuicao': distribuicao,
                            'total': total_distribuido,
                            'preco': produto.get('preco_38_percent', 0),
                            'valor_total_item': total_distribuido * pd.to_numeric(produto.get('preco_38_percent', 0), errors='coerce')
                        }
                        st.success(f"✅ Produto adicionado com {total_distribuido} unidades distribuídas!")
                        st.rerun()
            else:
                st.error(f"❌ Produto {codigo_add} não encontrado")

    else:
        # Modo 1→1: quantidade única
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            codigo_add = st.text_input("Código do produto", key='codigo_add_single')

        with col2:
            qtd_add = st.number_input("Quantidade", min_value=1, value=1, key='qtd_add_single')

        with col3:
            st.write("")  # Espaço
            st.write("")  # Espaço
            if st.button("➕ Adicionar", use_container_width=True):
                if codigo_add:
                    produto = next((p for p in produtos_filtrados if str(p.get('codigo')) == str(codigo_add)), None)

                    if produto:
                        estoque = produto.get('estoque_atual', 0)
                        une_origem_prod = produto.get('une_origem', unes_origem[0])

                        if qtd_add > estoque:
                            st.error(f"❌ Quantidade ({qtd_add}) > estoque ({estoque})")
                        else:
                            # NOVA FUNCIONALIDADE: Validar transferência com regras de negócio
                            with st.spinner("🔍 Validando transferência..."):
                                try:
                                    validacao = validar_transferencia_produto.invoke({
                                        "produto_id": int(codigo_add),
                                        "une_origem": int(une_origem_prod),
                                        "une_destino": int(unes_destino[0]),
                                        "quantidade": int(qtd_add)
                                    })

                                    if validacao.get('valido'):
                                        # Transferência válida - adicionar ao carrinho
                                        chave = f"{codigo_add}_UNE{une_origem_prod}"
                                        st.session_state.carrinho_transferencia[chave] = {
                                            'produto': produto,
                                            'une_origem': une_origem_prod,
                                            'distribuicao': {unes_destino[0]: qtd_add},
                                            'total': qtd_add,
                                            'preco': produto.get('preco_38_percent', 0),
                                            'valor_total_item': qtd_add * pd.to_numeric(produto.get('preco_38_percent', 0), errors='coerce'),
                                            'validacao': validacao  # Guardar validação
                                        }

                                        # Mostrar feedback com base na prioridade
                                        prioridade = validacao.get('prioridade', 'NORMAL')
                                        score = validacao.get('score_prioridade', 0)
                                        qtd_recomendada = validacao.get('quantidade_recomendada', qtd_add)

                                        if prioridade == 'URGENTE':
                                            st.error(f"🚨 **URGENTE** (Score: {score}/100)")
                                            st.warning(f"Produto adicionado. Quantidade recomendada: {qtd_recomendada}")
                                        elif prioridade == 'ALTA':
                                            st.warning(f"⚡ **ALTA PRIORIDADE** (Score: {score}/100)")
                                            st.info(f"Produto adicionado. Quantidade recomendada: {qtd_recomendada}")
                                        elif prioridade == 'NORMAL':
                                            st.success(f"✅ Produto adicionado (Prioridade: NORMAL, Score: {score}/100)")
                                        else:
                                            st.info(f"✅ Produto adicionado (Prioridade: {prioridade})")

                                        # Mostrar recomendações
                                        if validacao.get('recomendacoes'):
                                            with st.expander("💡 Recomendações"):
                                                for rec in validacao['recomendacoes']:
                                                    st.write(f"• {rec}")

                                        st.rerun()
                                    else:
                                        # Transferência inválida
                                        st.error(f"❌ Transferência não recomendada")
                                        st.warning(f"**Motivo:** {validacao.get('motivo', 'Validação falhou')}")

                                except Exception as e:
                                    # Fallback: adicionar sem validação se houver erro
                                    st.warning(f"⚠️ Não foi possível validar (sistema off-line): {str(e)[:100]}")
                                    chave = f"{codigo_add}_UNE{une_origem_prod}"
                                    st.session_state.carrinho_transferencia[chave] = {
                                        'produto': produto,
                                        'une_origem': une_origem_prod,
                                        'distribuicao': {unes_destino[0]: qtd_add},
                                        'total': qtd_add,
                                        'preco': produto.get('preco_38_percent', 0),
                                        'valor_total_item': qtd_add * pd.to_numeric(produto.get('preco_38_percent', 0), errors='coerce')
                                    }
                                    st.info(f"✅ Produto {codigo_add} adicionado (sem validação)")
                                    st.rerun()
                    else:
                        st.error(f"❌ Produto {codigo_add} não encontrado")
                else:
                    st.warning("⚠️ Digite o código do produto")

# --- CARRINHO DE TRANSFERÊNCIA ---
if st.session_state.carrinho_transferencia:
    st.markdown("---")
    st.subheader("🛒 Carrinho de Transferência")

    carrinho_items = []
    total_itens = 0
    total_valor = 0

    for chave, item in st.session_state.carrinho_transferencia.items():
        produto = item['produto']
        une_origem_item = item.get('une_origem', 'N/A')
        distribuicao = item.get('distribuicao', {})
        total_prod = item.get('total', 0)
        valor_total_item = item.get('valor_total_item', 0)
        validacao = item.get('validacao', {})

        # Criar string de distribuição
        dist_str = ", ".join([f"UNE {dest}: {qtd}" for dest, qtd in distribuicao.items() if qtd > 0])

        # Adicionar badge de prioridade se houver validação
        prioridade_badge = ""
        if validacao.get('prioridade'):
            prioridade = validacao['prioridade']
            score = validacao.get('score_prioridade', 0)
            if prioridade == 'URGENTE':
                prioridade_badge = f"🚨 URGENTE ({score:.0f})"
            elif prioridade == 'ALTA':
                prioridade_badge = f"⚡ ALTA ({score:.0f})"
            elif prioridade == 'NORMAL':
                prioridade_badge = f"✓ NORMAL ({score:.0f})"
            else:
                prioridade_badge = f"• {prioridade}"

        carrinho_items.append({
            'Código': produto.get('codigo'),
            'Produto': produto.get('nome_produto', 'N/A')[:30],
            'Origem': f"UNE {une_origem_item}",
            'Distribuição': dist_str,
            'Total': total_prod,
            'Prioridade': prioridade_badge if prioridade_badge else "N/A",
            'Valor Total': f"R$ {valor_total_item:,.2f}",
            'Estoque': produto.get('estoque_atual', 0)
        })
        total_itens += total_prod
        total_valor += valor_total_item

    df_carrinho = pd.DataFrame(carrinho_items)
    st.dataframe(df_carrinho, use_container_width=True, hide_index=True)

    st.info(f"📦 **{len(carrinho_items)}** produtos | **{total_itens}** unidades | **Valor Total: R$ {total_valor:,.2f}**")

    # Ações do carrinho
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗑️ Limpar Carrinho", use_container_width=True):
            st.session_state.carrinho_transferencia = {}
            st.rerun()

    with col2:
        codigo_remover = st.text_input("Remover produto (código)", key='codigo_remover')
        if st.button("➖ Remover", use_container_width=True) and codigo_remover:
            # Encontrar chave que contém o código
            chave_encontrada = None
            for chave in st.session_state.carrinho_transferencia.keys():
                if chave.startswith(str(codigo_remover)):
                    chave_encontrada = chave
                    break

            if chave_encontrada:
                del st.session_state.carrinho_transferencia[chave_encontrada]
                st.success(f"✅ Produto {codigo_remover} removido")
                st.rerun()
            else:
                st.error(f"❌ Produto {codigo_remover} não encontrado no carrinho")

    with col3:
        st.write("")  # Espaço

    # --- GERAR SOLICITAÇÃO ---
    st.markdown("---")
    st.subheader("📝 Finalizar Solicitação de Transferência")

    observacoes = st.text_area("Observações (opcional)", "", height=100)

    col1, col2 = st.columns(2)

    with col1:
        prioridade = st.selectbox("Prioridade", ["Normal", "Alta", "Urgente"])

    with col2:
        st.write("")  # Espaço
        st.write("")  # Espaço
        if st.button("✅ Gerar Solicitação", type="primary", use_container_width=True):
            # Gerar solicitação
            solicitacao = {
                'timestamp': datetime.now().isoformat(),
                'usuario': st.session_state.get('username', 'user'),
                'modo': modo_transferencia.split(' ')[0],
                'unes_origem': unes_origem,
                'unes_destino': unes_destino,
                'produtos': st.session_state.carrinho_transferencia,
                'total_produtos': len(carrinho_items),
                'total_itens': total_itens,
                'total_valor': total_valor,
                'prioridade': prioridade,
                'observacoes': observacoes,
                'status': 'PENDENTE'
            }

            # Salvar solicitação
            solicitacao_path = Path(__file__).parent.parent / 'data' / 'transferencias'
            solicitacao_path.mkdir(exist_ok=True)

            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transferencia_{timestamp_str}.json"

            with open(solicitacao_path / filename, 'w', encoding='utf-8') as f:
                json.dump(solicitacao, f, indent=2, ensure_ascii=False)

            origem_str = ", ".join([f"UNE {u}" for u in unes_origem])
            destino_str = ", ".join([f"UNE {u}" for u in unes_destino])

            st.success(f"""
            ✅ **Solicitação gerada com sucesso!**

            **Número:** {timestamp_str}
            **Modo:** {modo_transferencia.split(' ')[0]}
            **Origem:** {origem_str}
            **Destino:** {destino_str}
            **Total de produtos:** {len(carrinho_items)}
            **Total de unidades:** {total_itens}
            **Prioridade:** {prioridade}

            Arquivo salvo: `{filename}`
            """)

            # Limpar carrinho
            st.session_state.carrinho_transferencia = {}

            st.balloons()

else:
    st.info("🛒 Carrinho vazio. Adicione produtos para criar uma solicitação de transferência.")

# --- SUGESTÕES AUTOMÁTICAS ---
st.markdown("---")
st.subheader("🤖 Sugestões Automáticas de Transferências")

st.info("💡 **Dica:** Clique em '🔮 Gerar Sugestões' para analisar oportunidades de transferência baseadas em linha verde, MC e vendas")

# Filtros para geração de sugestões
with st.expander("⚙️ Filtros de Geração", expanded=False):
    st.caption("⚠️ **Importante:** Selecione os filtros ANTES de gerar sugestões. Após gerar, limpe o cache e regere para aplicar novos filtros.")

    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        filtro_segmento = st.selectbox(
            "Filtrar por segmento",
            ["Todos"] + sorted(segmentos) if 'segmentos' in locals() else ["Todos"],
            key='filtro_sug_segmento',
            help="Filtro visual: mostra apenas sugestões do segmento selecionado"
        )

    with col_f2:
        filtro_une_origem = st.selectbox(
            "Filtrar por UNE origem",
            ["Todas"] + [f"UNE {u}" for u in une_ids],
            key='filtro_sug_une_origem',
            help="Gera sugestões APENAS desta UNE origem (filtro na geração)"
        )

    with col_f3:
        limite_sugestoes = st.slider(
            "Limite de sugestões",
            min_value=5,
            max_value=50,
            value=10,
            step=5,
            key='limite_sug',
            help="Número máximo de sugestões a gerar"
        )

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # Mostrar cache info se existir
    if 'sugestoes_cache_timestamp' in st.session_state:
        from datetime import datetime
        cache_time = st.session_state.sugestoes_cache_timestamp
        tempo_cache = (datetime.now() - datetime.fromisoformat(cache_time)).total_seconds() / 60
        if tempo_cache < 5:
            st.caption(f"✅ Sugestões em cache (válido por mais {5 - int(tempo_cache):.0f} min)")
        else:
            st.caption("⚠️ Cache expirado - gere novas sugestões")

with col2:
    if st.button("🔮 Gerar Sugestões", use_container_width=True, type="primary"):
        with st.spinner("🤖 Analisando oportunidades de transferência..."):
            try:
                # Verificar cache (5 minutos)
                usar_cache = False
                if 'sugestoes_cache_timestamp' in st.session_state:
                    from datetime import datetime
                    cache_time = datetime.fromisoformat(st.session_state.sugestoes_cache_timestamp)
                    tempo_decorrido = (datetime.now() - cache_time).total_seconds()

                    # Cache válido por 5 minutos (300 segundos)
                    if tempo_decorrido < 300:
                        usar_cache = True
                        st.info("⚡ Usando sugestões do cache (atualizadas há menos de 5 min)")

                if not usar_cache:
                    # Preparar parâmetros para geração de sugestões
                    params = {"limite": limite_sugestoes}

                    # Aplicar filtro de UNE origem se selecionado
                    if 'filtro_sug_une_origem' in st.session_state and st.session_state.filtro_sug_une_origem != "Todas":
                        une_filtro = int(st.session_state.filtro_sug_une_origem.split()[-1])
                        params["une_origem_filtro"] = une_filtro

                    # Gerar sugestões com filtros
                    sugestoes_result = sugerir_transferencias_automaticas.invoke(params)

                    if 'error' in sugestoes_result:
                        st.error(f"❌ Erro: {sugestoes_result['error']}")
                    elif sugestoes_result.get('total_sugestoes', 0) == 0:
                        st.info("✓ Nenhuma oportunidade de transferência identificada no momento")
                        st.caption("Todas as UNEs estão com estoque balanceado!")
                    else:
                        # Guardar sugestões e timestamp no session_state
                        from datetime import datetime
                        st.session_state.sugestoes_transferencia = sugestoes_result
                        st.session_state.sugestoes_cache_timestamp = datetime.now().isoformat()
                        st.success(f"✓ {sugestoes_result['total_sugestoes']} sugestões geradas!")
                        st.rerun()
                else:
                    # Usar sugestões do cache
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Erro ao gerar sugestões: {str(e)[:200]}")

with col3:
    # Botão para limpar cache e forçar regeração
    if 'sugestoes_transferencia' in st.session_state:
        if st.button("🗑️ Limpar Cache", use_container_width=True, help="Limpa sugestões cacheadas"):
            if 'sugestoes_transferencia' in st.session_state:
                del st.session_state.sugestoes_transferencia
            if 'sugestoes_cache_timestamp' in st.session_state:
                del st.session_state.sugestoes_cache_timestamp
            st.success("✅ Cache limpo! Gere novas sugestões.")
            st.rerun()

# Mostrar sugestões se existirem
if 'sugestoes_transferencia' in st.session_state and st.session_state.sugestoes_transferencia:
    sugestoes_data = st.session_state.sugestoes_transferencia

    # Aplicar filtros de visualização
    sugestoes_filtradas = sugestoes_data.get('sugestoes', [])
    total_original = len(sugestoes_filtradas)

    # Aplicar filtro de segmento (usando variável correta do expander)
    if 'filtro_sug_segmento' in st.session_state and st.session_state.filtro_sug_segmento != "Todos":
        filtro_seg_aplicado = st.session_state.filtro_sug_segmento
        sugestoes_filtradas = [s for s in sugestoes_filtradas if s.get('segmento') == filtro_seg_aplicado]

    # Mostrar info sobre filtros aplicados
    if total_original != len(sugestoes_filtradas):
        st.caption(f"🔍 Filtros aplicados: {total_original} → **{len(sugestoes_filtradas)}** sugestões")

    # Recalcular estatísticas com filtros
    stats_filtradas = {
        'total': len(sugestoes_filtradas),
        'urgentes': len([s for s in sugestoes_filtradas if s.get('prioridade') == 'URGENTE']),
        'altas': len([s for s in sugestoes_filtradas if s.get('prioridade') == 'ALTA']),
        'normais': len([s for s in sugestoes_filtradas if s.get('prioridade') == 'NORMAL']),
        'total_unidades': sum(s.get('quantidade_sugerida', 0) for s in sugestoes_filtradas)
    }

    stats = stats_filtradas

    # Estatísticas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", stats.get('total', 0))
    with col2:
        st.metric("🚨 Urgentes", stats.get('urgentes', 0))
    with col3:
        st.metric("⚡ Altas", stats.get('altas', 0))
    with col4:
        st.metric("Unidades", stats.get('total_unidades', 0))

    # Tabela de sugestões
    st.markdown("### Top Sugestões")

    if not sugestoes_filtradas:
        st.info("Nenhuma sugestão encontrada com os filtros aplicados")

    for idx, sug in enumerate(sugestoes_filtradas, 1):
        prioridade = sug.get('prioridade', 'NORMAL')
        score = sug.get('score', 0)

        # Definir cor do expander baseado na prioridade
        if prioridade == 'URGENTE':
            header = f"🚨 #{idx} - {sug.get('nome_produto', 'N/A')[:40]} (Score: {score:.0f}/100)"
        elif prioridade == 'ALTA':
            header = f"⚡ #{idx} - {sug.get('nome_produto', 'N/A')[:40]} (Score: {score:.0f}/100)"
        else:
            header = f"✓ #{idx} - {sug.get('nome_produto', 'N/A')[:40]} (Score: {score:.0f}/100)"

        with st.expander(header):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**Transferência:**")
                st.write(f"UNE {sug.get('une_origem')} → UNE {sug.get('une_destino')}")
                st.write(f"**Quantidade:** {sug.get('quantidade_sugerida')} unidades")

            with col2:
                st.write("**Análise:**")
                st.write(f"Segmento: {sug.get('segmento', 'N/A')}")
                st.write(f"Prioridade: {prioridade}")
                st.write(f"Score: {score:.1f}/100")

            with col3:
                st.write("**Benefício:**")
                st.write(sug.get('beneficio_estimado', 'N/A'))

            if sug.get('motivo'):
                st.info(f"💡 **Motivo:** {sug['motivo']}")

            # Botão para adicionar ao carrinho
            if st.button(f"➕ Adicionar ao Carrinho", key=f"add_sug_{idx}"):
                # Adicionar sugestão ao carrinho automaticamente
                produto_id = sug.get('produto_id')
                une_origem = sug.get('une_origem')
                une_destino = sug.get('une_destino')
                quantidade = sug.get('quantidade_sugerida')

                # Buscar dados completos do produto
                produto_info = next((p for p in produtos_filtrados if str(p.get('codigo')) == str(produto_id)), None)

                if not produto_info:
                    # Tentar carregar produto específico do Parquet
                    try:
                        import pyarrow.parquet as pq
                        parquet_file = Path(__file__).parent.parent / 'data' / 'parquet' / 'admmat.parquet'

                        # Buscar produto específico (sem limite de 1000)
                        table = pq.read_table(
                            parquet_file,
                            columns=['codigo', 'nome_produto', 'estoque_atual', 'venda_30_d', 'preco_38_percent', 'nomesegmento', 'NOMEFABRICANTE'],
                            filters=[('une', '=', int(une_origem)), ('codigo', '=', int(produto_id))]
                        )
                        df = table.to_pandas()

                        if len(df) > 0:
                            produto_info = df.iloc[0].to_dict()
                    except:
                        produto_info = None

                if produto_info:
                    chave = f"{produto_id}_UNE{une_origem}"
                    st.session_state.carrinho_transferencia[chave] = {
                        'produto': produto_info,
                        'une_origem': une_origem,
                        'distribuicao': {une_destino: quantidade},
                        'total': quantidade,
                        'preco': produto_info.get('preco_38_percent', 0),
                        'valor_total_item': quantidade * pd.to_numeric(produto_info.get('preco_38_percent', 0), errors='coerce'),
                        'validacao': {
                            'valido': True,
                            'prioridade': prioridade,
                            'score_prioridade': score,
                            'quantidade_recomendada': quantidade
                        }
                    }
                    st.success(f"✅ Produto {produto_id} adicionado ao carrinho!")
                    st.rerun()
                else:
                    st.error(f"❌ Não foi possível carregar dados do produto {produto_id}")

    # Botão para limpar sugestões
    if st.button("🗑️ Limpar Sugestões"):
        del st.session_state.sugestoes_transferencia
        st.rerun()

# --- HISTÓRICO DE TRANSFERÊNCIAS ---
st.markdown("---")
st.subheader("📋 Histórico de Solicitações")

solicitacoes_path = Path(__file__).parent.parent / 'data' / 'transferencias'

if solicitacoes_path.exists():
    solicitacoes_files = sorted(solicitacoes_path.glob("transferencia_*.json"), reverse=True)

    if solicitacoes_files:
        st.info(f"📊 **{len(solicitacoes_files)}** solicitações encontradas")

        # Mostrar últimas 10
        for i, file in enumerate(solicitacoes_files[:10]):
            with open(file, 'r', encoding='utf-8') as f:
                sol = json.load(f)

            # Compatibilidade com formato antigo e novo
            unes_origem_sol = sol.get('unes_origem', [sol.get('une_origem')])
            unes_destino_sol = sol.get('unes_destino', [sol.get('une_destino')])

            origem_str = ", ".join([f"UNE {u}" for u in unes_origem_sol])
            destino_str = ", ".join([f"UNE {u}" for u in unes_destino_sol])
            modo_str = sol.get('modo', '1→1')

            with st.expander(f"📦 {file.stem} - {origem_str} → {destino_str} ({sol['status']})"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"**Data:** {sol['timestamp'][:16]}")
                    st.write(f"**Usuário:** {sol['usuario']}")
                    st.write(f"**Modo:** {modo_str}")

                with col2:
                    st.write(f"**Prioridade:** {sol['prioridade']}")
                    st.write(f"**Status:** {sol['status']}")

                with col3:
                    st.write(f"**Produtos:** {sol.get('total_produtos', len(sol['produtos']))}")
                    st.write(f"**Total unidades:** {sol['total_itens']}")
                    st.write(f"**Valor Total:** R$ {sol.get('total_valor', 0):,.2f}")

                if sol.get('observacoes'):
                    st.write(f"**Observações:** {sol['observacoes']}")

                # Detalhes dos produtos
                if st.checkbox(f"Ver produtos", key=f"ver_produtos_{i}"):
                    produtos_sol = []
                    for chave, item in sol['produtos'].items():
                        produto = item['produto']
                        une_origem_item = item.get('une_origem', 'N/A')
                        distribuicao = item.get('distribuicao', {item.get('une_destino', 'N/A'): item.get('quantidade', 0)})

                        dist_str = ", ".join([f"UNE {dest}: {qtd}" for dest, qtd in distribuicao.items() if qtd > 0])

                        produtos_sol.append({
                            'Código': produto.get('codigo'),
                            'Produto': produto.get('nome_produto', 'N/A')[:40],
                            'Origem': f"UNE {une_origem_item}",
                            'Distribuição': dist_str,
                            'Total': item.get('total', item.get('quantidade', 0))
                        })
                    st.dataframe(pd.DataFrame(produtos_sol), hide_index=True, use_container_width=True)
    else:
        st.info("📭 Nenhuma solicitação encontrada")
else:
    st.info("📭 Nenhuma solicitação encontrada")

# Footer
st.markdown("---")
st.caption(f"Agent_BI - Sistema de Transferências | Usuário: {st.session_state.get('username', 'N/A')} | Fonte: {adapter.get_status()['current_source'].upper()}")
