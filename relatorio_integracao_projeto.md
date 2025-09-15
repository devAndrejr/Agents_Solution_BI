### Relatório de Integração da Estrutura do Projeto Agent_BI

**Data:** 14 de setembro de 2025
**Autor:** Gemini

#### 1. Introdução

Este relatório descreve a estrutura integrada do projeto Agent_BI, um assistente de Inteligência de Negócios conversacional. A arquitetura é modular, baseada em agentes e projetada para processar consultas em linguagem natural, interagir com fontes de dados e fornecer respostas significativas, incluindo visualizações.

#### 2. Componentes Principais e Integração

O projeto Agent_BI é composto por diversos módulos e serviços que se integram para formar um sistema coeso:

*   **Frontend (Streamlit - `streamlit_app.py`, `pages/`):**
    *   **Função:** Interface de usuário interativa para o assistente conversacional e dashboards.
    *   **Integração:** Conecta-se ao backend FastAPI (`main.py`) para enviar consultas de usuário e receber respostas. Gerencia o estado da sessão (`st.session_state`) e o fluxo de autenticação (`core/auth.py`).

*   **API Gateway (FastAPI - `main.py`):**
    *   **Função:** Ponto de entrada centralizado para todas as requisições do frontend e outros serviços. Inicializa as dependências globais da aplicação.
    *   **Integração:** Na inicialização (`@app.on_event("startup")`), instancia o `OpenAILLMAdapter`, o `ParquetAdapter` (apontando para `data/parquet/admatao.parquet`) e o `CodeGenAgent`. Em seguida, constrói o `GraphBuilder` com esses adaptadores e agentes, compilando o grafo principal da aplicação (`app.state.agent_graph`). O endpoint `/api/v1/query` recebe as consultas do usuário e as invoca no grafo.

*   **Grafo de Agentes (LangGraph - `core/graph/graph_builder.py`, `core/agents/bi_agent_nodes.py`):**
    *   **Função:** O "cérebro" da aplicação. Uma máquina de estados finitos que orquestra o fluxo de processamento de consultas, roteando a requisição do usuário através de diferentes "nós" (agentes especializados).
    *   **Integração:**
        *   `GraphBuilder`: Recebe `llm_adapter`, `parquet_adapter` e `code_gen_agent` via injeção de dependência. Define os nós (`classify_intent`, `generate_parquet_query`, `execute_query`, `format_final_response`, etc.) e as arestas condicionais que determinam o fluxo com base na intenção do usuário e nos resultados intermediários.
        *   `bi_agent_nodes.py`: Contém a implementação de cada nó do grafo. Por exemplo, `classify_intent` usa o LLM para determinar a intenção, `generate_parquet_query` usa o LLM e o `ParquetAdapter` para gerar filtros, e `execute_query` usa o `ParquetAdapter` para buscar os dados.

*   **Adaptadores de Dados (`core/connectivity/parquet_adapter.py`):**
    *   **Função:** Fornece uma interface padronizada para acessar fontes de dados específicas. Atualmente, o `ParquetAdapter` é o principal adaptador de dados.
    *   **Integração:** O `ParquetAdapter` é instanciado em `main.py` e passado para o `GraphBuilder`. Ele é responsável por carregar o arquivo `admatao.parquet` e executar operações de filtragem e recuperação de esquema diretamente no DataFrame Pandas em memória.

*   **Ferramentas de Dados (`core/tools/data_tools.py`):**
    *   **Função:** Contém ferramentas reutilizáveis que os nós do grafo podem invocar.
    *   **Integração:** A ferramenta `fetch_data_from_query` foi modificada para aceitar filtros Parquet e utilizar o `ParquetAdapter`, garantindo que todas as consultas de dados passem por essa camada.

*   **Agente de Geração de Código (`core/agents/code_gen_agent.py`):**
    *   **Função:** Especializado em gerar e executar código Python para análises mais complexas ou visualizações.
    *   **Integração:** É instanciado em `main.py` e injetado no `GraphBuilder`. Seu prompt é configurado para instruir o LLM a usar o arquivo `admatao.parquet` e a variável `parquet_dir` para carregar dados. Ele utiliza um vector store (`data/vector_store.pkl`) e um catálogo limpo (`data/catalog_cleaned.json`) para RAG (Retrieval Augmented Generation), fornecendo contexto relevante ao LLM para a geração de código.

*   **Configuração (`core/config/settings.py`, `core/config/logging_config.py`):**
    *   **Função:** Centraliza o gerenciamento de variáveis de ambiente, credenciais e configurações de logging.
    *   **Integração:** `settings.py` carrega as configurações do arquivo `.env` e fornece strings de conexão e chaves de API. `logging_config.py` configura um sistema de logging robusto com handlers para console, arquivos de atividade, erros e interações do usuário. Ambos são inicializados no `main.py` e utilizados por diversos componentes.

*   **Catálogo de Dados (`data/catalog_cleaned.json`):**
    *   **Função:** Fornece metadados estruturados sobre as colunas dos arquivos Parquet, incluindo descrições e tipos de dados.
    *   **Integração:** É carregado pelo `generate_parquet_query` (e pelo `CodeGenAgent`) para enriquecer o prompt do LLM, permitindo que ele gere filtros e consultas mais precisas e contextualmente relevantes, utilizando os nomes de colunas padronizados.

#### 3. Fluxo de Consulta (Exemplo)

1.  **Usuário (Streamlit):** Envia uma pergunta (ex: "qual é o preço e o estoque linha verde maximo do produto 369947?").
2.  **API Gateway (FastAPI):** Recebe a requisição e a encaminha para o `app.state.agent_graph.invoke()`.
3.  **Nó `classify_intent`:** O LLM classifica a intenção (ex: `resposta_simples`).
4.  **Nó `generate_parquet_query`:** O LLM, usando o schema do `admatao.parquet` e as descrições do `catalog_cleaned.json`, gera um dicionário de filtros (ex: `{'codigo': 369947}`).
5.  **Nó `execute_query`:** A ferramenta `fetch_data_from_query` é invocada com o dicionário de filtros e o `ParquetAdapter`.
6.  **`ParquetAdapter`:** Carrega o `admatao.parquet`, aplica o filtro e retorna os dados correspondentes.
7.  **Nó `format_final_response`:** Os dados brutos são formatados (tratando `NaN`s) e encapsulados em uma resposta JSON.
8.  **API Gateway (FastAPI):** Retorna a resposta JSON para o frontend.
9.  **Frontend (Streamlit):** Exibe a resposta ao usuário.

#### 4. Conclusão

A estrutura do projeto Agent_BI demonstra uma arquitetura bem integrada e modular. As recentes refatorações e a transição para o uso exclusivo de arquivos Parquet (`admatao.parquet`) como fonte de dados principal foram implementadas com sucesso, garantindo que todos os componentes relevantes estejam alinhados. A utilização de um catálogo de dados limpo e a injeção de dependências contribuem para a robustez e manutenibilidade do sistema. O projeto está configurado para processar consultas complexas e fornecer respostas precisas, utilizando as capacidades de LLMs e análise de dados.

---
