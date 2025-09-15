PROMPT MESTRE: IMPLEMENTAÇÃO DA ARQUITETURA AVANÇADA DO AGENT_BI
1. PERSONA E PAPEL
QUEM VOCÊ É:
Você é um Arquiteto de Software Sênior e Engenheiro de IA, especialista em migrar sistemas de agentes complexos para arquiteturas LangGraph robustas, seguindo o padrão de Máquina de Estados Finitos. A sua missão é refatorar um projeto existente para um estado de excelência técnica, focando em modularidade, eficiência (mínimo de chamadas ao LLM), e desacoplamento total entre backend e frontend.

2. CONTEXTO E OBJETIVO GERAL
A SITUAÇÃO ATUAL:
Estou a finalizar a refatoração do projeto Agent_BI. O projeto já passou por uma limpeza estrutural, mas a lógica de orquestração inteligente do sistema antigo (supervisor_agent) foi substituída por um agente placeholder (caculinha_bi_agent), resultando na perda de funcionalidade. O objetivo agora é realizar a refatoração final e definitiva, implementando a "Arquitetura Avançada" que foi proposta em relatórios de análise anteriores (fornecidos abaixo).

MEU OBJETIVO FINAL:
Obter o código-fonte completo e funcional para os componentes chave da nova arquitetura. O sistema final deve:
Orquestrar todo o fluxo de tarefas através de um StateGraph no LangGraph.
Utilizar o LLM de forma mínima, apenas para classificação de intenção e geração de código complexo.
Implementar o fluxo de UX avançado para gráficos: desambiguação com o utilizador e geração de uma especificação JSON para o Plotly.js.
Ter uma clara separação entre a API de backend (FastAPI) e a interface de utilizador (Streamlit).

3. TAREFA ESPECÍFICA E IMEDIATA
SUA TAREFA AGORA:
Com base em todos os relatórios e no código-fonte atual fornecido, gere os seguintes cinco (5) ficheiros Python, que constituirão o núcleo da nova aplicação. Siga rigorosamente as melhores práticas de design de software.
1. core/tools/data_tools.py (As Ferramentas Simples):
Crie uma ferramenta (@tool) chamada fetch_data_from_query.
A sua única responsabilidade é receber uma query SQL como string, executá-la usando o DatabaseAdap...
[truncated]
# Relatório Completo de Arquivos do Projeto Agent_BI

Este documento fornece um resumo de cada arquivo no projeto, organizado por diretório.

## Diretório Raiz: `C:\Users\André\Documents\Agent_BI\`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `.env.example` | Arquivo de exemplo para variáveis de ambiente, contendo placeholders para chaves de API e nomes de modelo. |
| `.gitignore` | Especifica arquivos e diretórios que o Git deve ignorar, como ambientes virtuais, arquivos de cache e logs. |
| `README.md` | A documentação principal do projeto, incluindo descrição, instruções de configuração, visão geral da arquitetura e roadmap futuro. |
| `alembic.ini` | Arquivo de configuração para o Alembic, uma ferramenta de migração de banco de dados para SQLAlchemy. |
| `apresentacao_caculinha_bi.py` | Um arquivo de aplicação Streamlit que parece ser uma apresentação sobre o projeto "Caçulinha BI". |
| `apresentacao_diretoria_standalone.py` | Uma aplicação Streamlit autônoma para uma apresentação à diretoria. |
| `erro.txt` | Um arquivo de texto contendo um traceback Python, indicando um `ValueError` na aplicação Streamlit. |
| `generated_code.txt` | Um arquivo de texto contendo um script Python que usa pandas e Plotly para gerar um gráfico a partir de um arquivo Parquet. |
| `inspect_data_relationship.py` | Um script Python para analisar relacionamentos em um arquivo Parquet usando pandas. |
| `product_agent.py` | Um script Python que define a classe `ProductAgent` para consultar e analisar dados de produtos de arquivos Parquet. |
| `prompt.md` | Um arquivo markdown contendo um prompt para o Gemini gerar uma aplicação Streamlit com funcionalidades específicas. |
| `prompt.txt` | Um arquivo de texto contendo um prompt para um assistente de IA ajudar com um problema de código Python relacionado a LangChain e Streamlit. |
| `prompt_analise.txt` | Um arquivo de texto contendo um prompt para um revisor técnico analisar o projeto Agent BI. |
| `pytest.ini` | Arquivo de configuração para o pytest, definindo o `pythonpath`. |
| `relatorio.txt` | Um arquivo de texto contendo uma análise técnica e recomendações de simplificação para o projeto Agent BI. |
| `relatorio_final_refatoracao.txt`| Um arquivo de texto com o relatório final sobre a refatoração e unificação da arquitetura do projeto. |
| `relatorio_refatoracao.txt` | Um arquivo de texto com um relatório sobre o processo de refatoração, baseado em um "Plano C". |
| `requirements.in` | Um arquivo de entrada para `pip-compile` que lista as dependências diretas do projeto. |
| `requirements.txt` | O arquivo com a lista de todos os pacotes Python necessários para o projeto, gerado a partir de `requirements.in`. |
| `run_app.py` | Um script Python para executar a aplicação inteira, incluindo o backend FastAPI e um servidor de desenvolvimento de frontend. |
| `run_refactored_app.py` | Um script Python que demonstra como executar a aplicação refatorada, mostrando o padrão de injeção de dependência. |
| `streamlit_app.py` | O ponto de entrada principal para a interface de usuário Streamlit da aplicação Agent BI. |
| `streamlit_teste_novo.py` | Um arquivo de aplicação Streamlit para testar uma nova UI com `streamlit-shadcn-ui`. |
| `style.css` | Um arquivo CSS contendo estilos para a aplicação Streamlit. |

## Diretório Core: `C:\Users\André\Documents\Agent_BI\core\`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `__init__.py` | Arquivo vazio que marca o diretório `core` como um pacote Python. |
| `agent_state.py` | Define a estrutura de estado (`AgentState`) para o grafo de agentes, usando `TypedDict` para gerenciar mensagens, dados e decisões de roteamento. |
| `auth.py` | Gerencia a autenticação de usuários para a aplicação Streamlit, incluindo o formulário de login e a lógica de expiração de sessão. |
| `data_updater.py` | Contém a lógica para atualizar arquivos Parquet a partir de um banco de dados SQL Server. |
| `llm_adapter.py` | Implementa um adaptador para a API da OpenAI (`OpenAILLMAdapter`), lidando com a comunicação, tratamento de erros e retentativas. |
| `llm_base.py` | Define a classe base abstrata (`BaseLLMAdapter`) para adaptadores de LLM, estabelecendo um contrato para a implementação de `get_completion`. |
| `llm_langchain_adapter.py` | Adapta o `OpenAILLMAdapter` para ser compatível com a interface `BaseChatModel` do LangChain, permitindo sua integração em grafos LangChain. |
| `main.py` | Ponto de entrada para o backend FastAPI, que expõe endpoints para autenticação, processamento de queries e um agendador de tarefas para o pipeline de dados. |
| `query_processor.py` | Atua como o ponto de entrada para o processamento de consultas, delegando a tarefa para o `SupervisorAgent` para orquestração. |
| `run.py` | Um script principal para executar o agente em modo de linha de comando, permitindo interação direta com o `ToolAgent`. |
| `schemas.py` | Define os esquemas Pydantic para a aplicação, incluindo modelos para tokens, usuários e as requisições/respostas da API de consulta. |
| `security.py` | Contém a lógica de segurança para a API FastAPI, incluindo a criação e verificação de tokens JWT e a dependência `get_current_user`. |
| `session_state.py` | Centraliza as chaves usadas para gerenciar o estado da sessão no Streamlit, como `messages` e `authenticated`. |
| `transformer_adapter.py` | Arquivo vazio, possivelmente um placeholder para um futuro adaptador de modelo Transformer. |

### Subdiretório: `core/adapters`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `database_adapter.py` | Arquivo vazio, provavelmente um placeholder para um futuro adaptador de banco de dados. |

### Subdiretório: `core/agents`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `__init__.py` | Inicializa o pacote de agentes e a configuração de logging. |
| `base_agent.py` | Define a classe `BaseAgent`, que serve como base para outros agentes, fornecendo funcionalidades de processamento de consultas e logging. |
| `caculinha_bi_agent.py` | Cria um agente de BI substituto e suas ferramentas, com um adaptador de banco de dados injetado, e define a lógica para seleção de ferramentas e geração de consultas. |
| `caculinha_dev_agent.py` | Define o `CaculinhaDevAgent`, um agente especializado em desenvolvimento de código, que pode processar consultas relacionadas a código e sugerir melhorias. |
| `code_gen_agent.py` | Define o `CodeGenAgent`, que é especializado em gerar e executar código Python para análise de dados, utilizando RAG com FAISS para encontrar colunas relevantes. |
| `product_agent.py` | Define o `ProductAgent`, responsável por consultas e análises relacionadas a produtos, utilizando arquivos Parquet como fonte de dados. |
| `prompt_loader.py` | Contém a classe `PromptLoader`, responsável por carregar, listar e salvar prompts de arquivos JSON. |
| `supervisor_agent.py` | Define o `SupervisorAgent`, que roteia as consultas do usuário para o agente especialista apropriado (`ToolAgent` ou `CodeGenAgent`) com base na complexidade da consulta. |
| `tool_agent.py` | Define o `ToolAgent`, que utiliza um conjunto de ferramentas predefinidas (via LangChain) para responder a perguntas diretas sobre os dados. |

### Subdiretório: `core/api`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `__init__.py` | Inicializa o pacote da API Flask, registra as rotas dos blueprints e define um endpoint de status. |
| `run_api.py` | Ponto de entrada para executar a aplicação Flask, configurando Swagger, Talisman (para segurança) e SocketIO. |

#### `core/api/routes`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `chat_routes.py` | Define os endpoints da API para o processamento de mensagens de chat, incluindo o endpoint principal `/api/chat` e um para upload de arquivos. |
| `frontend_routes.py` | Define as rotas para a interface web (frontend) baseada em Flask, incluindo login, dashboard, perfil e outras páginas, além de endpoints de API para o chat. |
| `product_routes.py` | Define os endpoints da API para consultas relacionadas a produtos, como busca, detalhes, histórico de vendas e análise. |
| `query_routes.py` | Um blueprint principal que agrega e registra os sub-blueprints de rotas de consulta (`consulta`, `historico`, `analise`). |
| `query_routes_analise.py` | Define os endpoints da API para análises específicas, como vendas e estoque por categoria. |
| `query_routes_consulta.py` | Define os endpoints da API para consultas gerais, como saudações, busca de produtos por código e top produtos vendidos. |
| `query_routes_historico.py` | Define os endpoints da API para consultas de histórico, como o histórico de vendas de um produto específico. |

### Subdiretório: `core/config`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `__init__.py` | Marca o diretório `core/config` como um pacote Python, permitindo importações mais limpas. |
| `config.py` | Define uma classe `Config` que centraliza a configuração do projeto, carregando variáveis de um arquivo `.env`. |
| `logging_config.py` | Configura o logging para a aplicação, incluindo diferentes handlers (console, arquivo) and formatters (simples, JSON). |
| `settings.py` | Utiliza `pydantic-settings` para criar uma classe de configuração centralizada e validada, que carrega variáveis de ambiente e constrói strings de conexão. |

#### `core/config/interfaces`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `config_interface.py` | Define uma interface abstrata (`ConfigInterface`) para padronizar o acesso às configurações do sistema. |

### Subdiretório: `core/connectivity`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `base.py` | Define a classe base abstrata (`DatabaseAdapter`) para adaptadores de banco de dados, estabelecendo um contrato comum para todas as implementações de conectividade. |
| `sql_server_adapter.py` | Implementa a interface `DatabaseAdapter` para o Microsoft SQL Server, gerenciando a conexão e a execução de consultas. |

### Subdiretório: `core/database`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `__init__.py` | Marca o diretório `core/database` como um pacote Python. |
| `database.py` | Arquivo vazio, provavelmente um placeholder para futuras funcionalidades de banco de dados. |
| `models.py` | Define o modelo de dados `User` para a tabela `usuarios` usando SQLAlchemy, descrevendo suas colunas e tipos. |
| `sql_server_auth_db.py` | Contém toda a lógica de autenticação de usuários com o banco de dados SQL Server, incluindo criação, autenticação, bloqueio de contas e redefinição de senha. |

### Subdiretório: `core/factory`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `component_factory.py` | Implementa o padrão de design Factory para criar e gerenciar instâncias de vários componentes do sistema, como adaptadores MCP e agentes. |

### Subdiretório: `core/graph`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `__init__.py` | Marca o diretório `core/graph` como um pacote Python. |
| `agent.py` | Define o `GraphAgent`, responsável por orquestrar o LLM e as ferramentas, criando o `Agent Runnable` com um prompt de sistema dinâmico. |
| `graph_builder.py` | Constrói o grafo de execução do LangGraph (`StateGraph`), definindo os nós, as arestas e a lógica condicional para rotear as tarefas entre os agentes e as ferramentas. |

### Subdiretório: `core/mcp`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `__init__.py` | Inicializa o pacote MCP (Multi-Cloud Processing) e exporta os adaptadores. |
| `mcp_manager.py` | Gerencia o processamento distribuído em múltiplas nuvens, carregando configurações de provedores e orquestrando a execução de consultas. |
| `mock_data.py` | Arquivo vazio, provavelmente um placeholder para futuros dados mockados para testes. |
| `query_adapter.py` | Atua como uma ponte entre o processador de consultas existente e o sistema MCP, adaptando os resultados para o formato esperado. |
| `sqlserver_adapter.py` | Adaptador MCP para SQL Server, que implementa o processamento distribuído utilizando recursos nativos do SQL Server. |
| `sqlserver_mcp_adapter.py` | Atua como um wrapper para o `sqlserver_adapter`, adaptando-o para a interface padrão `AdaptadorMCPInterface`. |

#### `core/mcp/interfaces`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `mcp_adapter_interface.py` | Define a interface abstrata (`MCPAdapterInterface`) para padronizar a comunicação com serviços externos através de adaptadores MCP. |

### Subdiretório: `core/orchestration`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `supervisor.py` | Define a classe `Supervisor`, que atua como o orquestrador principal, recebendo dependências (como `Settings` e `DatabaseAdapter`) e executando tarefas. |

### Subdiretório: `core/prompts`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `analise_de_projeto.md` | Contém um prompt detalhado para uma IA atuar como Arquiteto de Soluções e Gerente de Produto Sênior, com o objetivo de analisar o PRD do projeto Agent_BI e gerar um relatório estratégico. |

### Subdiretório: `core/tools`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `__init__.py` | Arquivo vazio que marca o diretório `core/tools` como um pacote Python. |
| `check_gui_dependencies.py` | Um script para verificar se todas as dependências necessárias para a interface gráfica estão instaladas. |
| `check_integration.py` | Arquivo vazio, provavelmente um placeholder para um futuro script de verificação de integração. |
| `data_tools.py` | Define ferramentas para consultar dados de arquivos Parquet, como `list_table_columns` e `query_product_data`. |
| `debug_server.py` | Um script para depurar o servidor, verificando importações e configurações. |
| `graph_integration.py` | Contém lógica para processar a resposta de um agente e gerar um gráfico, se apropriado. |
| `mcp_sql_server_tools.py` | Define um conjunto de ferramentas (`sql_tools`) para interagir com os dados de produtos, como obter dados de produtos, estoque e histórico de vendas. |
| `sql_server_tools.py` | Arquivo vazio, provavelmente um placeholder para futuras ferramentas de SQL Server. |
| `verify_imports.py` | Um script para verificar se as importações críticas do projeto funcionam corretamente. |

### Subdiretório: `core/utils`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `__init__.py` | Marca o diretório `core/utils` como um pacote Python. |
| `chart_generator.py` | Define a classe `ChartGenerator` para criar vários tipos de gráficos (vendas, produtos, categorias) usando Plotly. |
| `context.py` | Define uma variável de contexto (`correlation_id_var`) para armazenar um ID de correlação para rastreamento de logs. |
| `correlation_id.py` | Define um filtro de logging (`CorrelationIdFilter`) que adiciona um ID de correlação a cada registro de log. |
| `db_check.py` | Arquivo vazio, provavelmente um placeholder para um futuro script de verificação de banco de dados. |
| `db_config.py` | Define configurações relacionadas ao banco de dados, como mapeamento de tabelas e consultas SQL pré-definidas. |
| `db_connection.py` | Cria um engine SQLAlchemy com um pool de conexões e fornece uma função para obter uma conexão com o banco de dados. |
| `db_fallback.py` | Implementa um mecanismo de fallback e retry com backoff exponencial para operações de banco de dados. |
| `db_structure_loader.py` | Contém uma função para carregar a estrutura do banco de dados a partir de um arquivo JSON. |
| `db_utils.py` | Fornece funções utilitárias para interagir com os dados, como obter um DataFrame de uma tabela e preparar dados para gráficos. |
| `directory_setup.py` | Contém uma função para configurar os diretórios necessários para a aplicação. |
| `env_setup.py` | Define uma função para carregar arquivos `.env` de diferentes locais do projeto. |
| `event_manager.py` | Arquivo vazio, provavelmente um placeholder para um futuro gerenciador de eventos. |
| `langchain_utils.py` | Fornece uma função utilitária para obter um modelo LangChain configurado. |
| `openai_config.py` | Contém uma função placeholder para configurar o cliente da OpenAI. |
| `query_history.py` | Define a classe `QueryHistory` para gerenciar o histórico de consultas, salvando-o em arquivos JSON diários. |
| `security.py` | Contém uma função para sanitizar consultas SQL, removendo comentários e espaços extras. |
| `security_utils.py` | Fornece funções utilitárias de segurança, como `verify_password` e `get_password_hash`, usando `passlib`. |
| `session_manager.py` | Define a classe `SessionManager` para gerenciar sessões de usuário, incluindo criação, obtenção de dados e adição de mensagens. |
| `sql_utils.py` | Fornece funções utilitárias para trabalhar com SQL, como obter a string de conexão, verificar operações proibidas e executar consultas. |
| `text_utils.py` | Contém funções para formatar valores como moeda, números e datas para o local brasileiro. |
| `validators.py` | Arquivo vazio, provavelmente um placeholder para futuras funções de validação. |

## Diretório: `dags`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `pipeline_dados_caculinha.py` | Define a sequência de execução (blueprint) do pipeline de dados, que inclui exportar dados do SQL Server para Parquet, limpar e unir os arquivos Parquet. |

## Diretório: `data`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `CATALOGO_PARA_EDICAO.json` | Um catálogo de dados JSON para ser editado por usuários de negócio, com o objetivo de refinar as descrições das colunas e melhorar a inteligência do agente. |
| `COMO_EDITAR_O_CATALOGO.md` | Um guia em markdown que explica como editar o arquivo `CATALOGO_PARA_EDICAO.json` para refinar o catálogo de dados. |
| `catalog_focused.json` | Um catálogo de dados JSON focado, provavelmente uma versão mais limpa ou específica do catálogo principal. |
| `config.json` | Um arquivo de configuração JSON para o banco de dados, API e logging. |
| `data_catalog.json` | Um catálogo de dados JSON que descreve os arquivos Parquet, seus esquemas e colunas. |
| `data_catalog_enriched.json` | Uma versão enriquecida do catálogo de dados, provavelmente com descrições mais detalhadas. |
| `database_structure.json` | Um arquivo JSON que descreve a estrutura do banco de dados, incluindo tabelas, colunas e tipos de dados. |
| `db_context.json` | Um arquivo JSON que fornece contexto sobre o banco de dados, incluindo tabelas e relacionamentos. |
| `mcp_config.json` | Um arquivo de configuração JSON para o MCP (Multi-Cloud Processing), definindo provedores de nuvem e suas configurações. |
| `prompt_modular_vibe_coding.json` | Um prompt JSON que define a persona, ferramentas e estilo de comunicação para um assistente de desenvolvimento de software. |
| `prompt_modular_vibe_coding_project.json` | Uma versão do prompt anterior com recomendações específicas para o projeto. |
| `sqlserver_mcp_config.json` | Um arquivo de configuração JSON específico para o adaptador MCP do SQL Server. |
| `vector_store.pkl` | Um arquivo pickle que armazena um vector store, provavelmente para uso em RAG (Retrieval-Augmented Generation). |

## Diretório: `docs`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `arquitetura_alvo.md` | Descreve a arquitetura alvo para o projeto, visando um sistema de BI conversacional robusto, modular e escalável. |
| `prd.md` | Documento de Requisitos do Produto (PRD) que descreve os requisitos, funcionalidades e o propósito do Agent_BI. |

### Subdiretório: `docs/archive`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `guia_integracao_ia_dados.md` | Um guia para integrar a IA com os dados do projeto. |
| `Instrucoes.md` | Um arquivo de instruções para o projeto. |
| `mcp_sqlserver_readme.md` | Um arquivo README para o adaptador MCP do SQL Server. |
| `relatorio_arquitetura_final.md` | Um relatório final sobre a arquitetura do projeto. |
| `relatorio_de_integracao.md` | Um relatório sobre a integração dos componentes do projeto. |

## Diretório: `migrations`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `env.py` | Script de configuração do Alembic que define como as migrações são executadas, conectando-se ao banco de dados e especificando o metadata do modelo. |
| `script.py.mako` | Template Mako usado pelo Alembic para gerar novos arquivos de script de migração. |

### Subdiretório: `migrations/versions`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `d4f68a172d44_create_user_table.py` | Script de migração do Alembic que define as operações de `upgrade` e `downgrade` para o banco de dados, neste caso, removendo e recriando tabelas. |

## Diretório: `pages`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `2_Dashboard.py` | Define a página "Dashboard" da aplicação Streamlit, que permite visualizar e organizar gráficos personalizados. |
| `3_Monitoramento.py` | Define a página "Monitoramento" da aplicação Streamlit, que exibe logs do sistema e o status dos serviços. |
| `4_Área_do_Comprador.py` | Define a página "Área do Comprador" da aplicação Streamlit, que permite a gestão do catálogo de dados. |
| `5_Painel_de_Administração.py` | Define a página "Painel de Administração" da aplicação Streamlit, para gerenciamento de usuários. |
| `6_Gerenciar_Catalogo.py` | Define a página "Gerenciar Catálogo" da aplicação Streamlit, que permite aos administradores gerenciar o catálogo de dados. |

## Diretório: `scripts`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `agente_atualizador.py` | Um agente que agenda e executa o script de exportação de dados do SQL Server para Parquet. |
| `analisar_integracao.py` | Script para acionar a análise de integração do projeto e gerar um relatório. |
| `carregar_dados_excel.py` | Script para carregar dados de um arquivo Excel para o banco de dados SQL Server. |
| `check_mcp_online.py` | Verifica se o MCP (Multi-Cloud Processing) está online e respondendo. |
| `clean_final_data.py` | Script para forçar colunas potencialmente numéricas em um arquivo Parquet a serem numéricas. |
| `clean_parquet_data.py` | Limpa os arquivos Parquet, normalizando nomes de colunas e otimizando tipos de dados. |
| `cleanup_project.py` | Identifica e gera um script para deletar arquivos e diretórios desnecessários do projeto. |
| `criar_usuario.py` | Script de linha de comando para criar um novo usuário no banco de dados de autenticação. |
| `data_pipeline.py` | Pipeline de dados para extrair dados do SQL Server e salvá-los como arquivos Parquet. |
| `delete_unnecessary_files.bat` | Um script de lote do Windows para deletar arquivos e diretórios desnecessários. |
| `enrich_catalog.py` | Lê o catálogo de dados, gera descrições iniciais e salva em um novo arquivo. |
| `evaluate_agent.py` | Script para avaliar o `QueryProcessor` com uma lista de consultas pré-definidas. |
| `export_sqlserver_to_parquet.py` | Exporta todas as tabelas de um banco de dados SQL Server para arquivos Parquet. |
| `final_cleanup_temp.py` | Arquivo vazio, provavelmente um placeholder para um futuro script de limpeza. |
| `fix_database_connection.py` | Script para diagnosticar e corrigir problemas de conexão com o banco de dados. |
| `fix_parquet_encoding.py` | Corrige os nomes das colunas de um arquivo Parquet e o salva novamente. |
| `formatador.py` | Um script para formatar o código Python usando `black` ou `ruff`. |
| `generate_data_catalog.py` | Gera um catálogo de dados JSON a partir dos arquivos Parquet no diretório `data/parquet_cleaned`. |
| `generate_db_html.py` | Gera uma visualização HTML da estrutura do banco de dados. |
| `generate_embeddings.py` | Carrega o catálogo de dados, gera embeddings para as descrições das colunas e os salva em um índice FAISS. |
| `gerar_estrutura.py` | Gera uma representação em árvore da estrutura de um diretório. |
| `gerar_limpeza.py` | Gera um relatório de limpeza da arquitetura, classificando os arquivos a serem movidos, excluídos ou revisados. |
| `iniciar_mcp_sqlserver.py` | Configura o ambiente e o banco de dados SQL Server para o MCP. |
| `inspect_admat_parquet.py` | Script para inspecionar as colunas de um arquivo Parquet específico. |
| `inspect_admmatao_data.py` | Script para inspecionar os dados de um arquivo Parquet específico, incluindo a verificação de um produto específico. |
| `inspect_parquet_quality.py` | Analisa a estrutura, tipos de dados e qualidade de todos os arquivos Parquet no diretório `data/parquet`. |
| `inspect_segment.py` | Inspeciona as categorias de um segmento específico em um arquivo Parquet. |
| `integrador_componentes.py` | Integra componentes desconectados ao projeto principal, analisando dependências e sugerindo modificações. |
| `integration_mapper.py` | Mapeia as integrações e o uso de componentes em todo o projeto para identificar código obsoleto. |
| `investigador.py` | Gera um relatório completo da estrutura e dependências do projeto. |
| `limpeza_arquitetura.md` | Um relatório de limpeza da arquitetura, com uma lista de arquivos a serem excluídos ou revisados. |
| `limpeza_avancada.py` | Gera um relatório de limpeza e exclui arquivos e pastas com a confirmação do usuário. |
| `limpeza_venv.ps1` | Um script PowerShell para limpar e reinstalar pacotes em um ambiente virtual. |
| `lint_automate.py` | Automatiza o processo de linting e formatação de código usando `autoflake`, `black` e `isort`. |
| `melhorador_coesao.py` | Melhora a coesão do código, reorganizando os módulos com base na análise de dependências e similaridade funcional. |
| `merge_catalogs.py` | Mescla o catálogo de dados gerado com o catálogo focado. |
| `merge_parquets.py` | Concatena vários arquivos Parquet em um único DataFrame mestre. |
| `padronizar_colunas.py` | Padroniza os nomes das colunas de todos os arquivos Parquet em um diretório para snake_case. |
| `read_parquet_temp.py` | Arquivo vazio, provavelmente um placeholder para um futuro script de leitura de Parquet. |
| `rebuild_clean_data.py` | Lê um arquivo Parquet bruto, o limpa, adiciona a coluna `COMPRADOR` e o salva como uma nova fonte de verdade. |
| `rename_all_columns_final.py` | Corrige sistematicamente os erros de codificação nos nomes das colunas de um arquivo Parquet. |
| `restructure_parquet.py` | Reestrutura os arquivos Parquet de origem para corresponder ao esquema de um arquivo de destino. |
| `run_tests_modified.py` | Executa os testes do projeto, iniciando e parando um servidor Flask. |
| `run_tests_with_server.py` | Executa os testes do projeto, iniciando e parando um servidor Flask. |
| `run_testsprite.py` | Script para executar o TestSprite para testes de frontend. |
| `setup_database_indexes.sql` | Script SQL para configurar índices no banco de dados para otimizar a performance das consultas. |
| `setup_database_optimization.py` | Script para otimizar o banco de dados, executando o script de configuração de índices e testando a performance. |
| `setup_mcp_sqlserver.sql` | Script SQL para configurar as stored procedures para o MCP (Multi-Cloud Processing) no SQL Server. |
| `upload_parquet_to_sql.py` | Script para carregar dados de um arquivo Parquet para uma tabela do SQL Server usando `bcp`. |
| `venv_audit.py` | Gera um relatório de dependências do ambiente virtual, incluindo um gráfico interativo. |
| `venv_dependency_report.html` | Um relatório HTML contendo um gráfico de dependências da venv e uma lista de conflitos. |

## Diretório: `tests`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `check_db.py` | Um script de teste para verificar a conexão com o banco de dados. |
| `conftest.py` | Arquivo de configuração do Pytest que define fixtures para a aplicação Flask, como `app`, `client` e `runner`. |
| `temp_get_product_price.py` | Um script temporário para obter o preço de um produto específico de um arquivo Parquet. |
| `test_auth_db_init.py` | Testa a inicialização do banco de dados de autenticação. |
| `test_code_gen_agent.py` | Contém testes unitários para o `CodeGenAgent`, verificando se ele gera e executa código corretamente. |
| `test_db_connection.py` | Testa a conexão com o banco de dados SQL Server. |
| `test_openai_connection.py` | Testa a conexão com a API da OpenAI. |
| `test_real_queries.py` | Contém testes de integração para o `QueryProcessor`, simulando consultas reais e verificando os tipos de resposta. |
| `test_suite_completa.py` | Uma suíte de testes completa que inclui testes de unidade e integração para vários componentes do projeto. |
| `test_supervisor_agent.py` | Contém testes unitários para o `SupervisorAgent`, verificando se ele roteia as consultas corretamente. |
| `test_tool_agent.py` | Contém testes de integração para o `ToolAgent`, verificando se ele descreve suas ferramentas corretamente. |

## Diretório: `ui`

| Arquivo | Resumo da Finalidade |
| --- | --- |
| `__init__.py` | Arquivo vazio que marca o diretório `ui` como um pacote Python. |
| `ui_components.py` | Contém funções utilitárias para a interface do usuário Streamlit, como gerar links para download de imagens e CSVs, e aplicar customizações a gráficos Plotly. |
[DOCUMENTO 2: RELATÓRIO DE ANÁLISE ESTRATÉGICA]
Compreendi o seu desafio e o objetivo estratégico para o **Agent_BI**. A dificuldade na geração de gráficos conversacionais é um ponto de inflexão crítico que pode definir o sucesso ou o fracasso do produto. A seguir, apresento um relatório de análise detalhado, seguindo a estrutura solicitada e atuando na persona de Arquiteto de Soluções e Gerente de Produto Sênior.

---

## **Relatório de Análise Estratégica e Técnica: Agent_BI**

**Para:** Líder Técnico do Projeto
**De:** Arquiteto de Soluções & Gerente de Produto Sênior
**Data:** 2025-09-09
**Assunto:** Análise do PRD v1.0 com foco na implementação de gráficos conversacionais.

### **1. Análise Geral do Produto**

A visão do Agent_BI é forte e alinhada a uma dor de mercado clara e persistente: a latência entre a necessidade de um insight e sua obtenção. A democratização do acesso aos dados através de uma interface conversacional é uma proposta de valor poderosa.

*   **Pontos Fortes:**
    *   **Problema Bem Definido:** O PRD articula com clareza o problema da dependência de equipes técnicas (Seção 1.2), o que valida a necessidade do produto.
    *   **Público-Alvo Abrangente:** As personas (Seção 3) cobrem desde o nível estratégico (Carlos, o Diretor) até o operacional (Beatriz, a Compradora), mostrando um grande potencial de impacto organizacional.
    *   **Metas Mensuráveis:** As metas de negócio e de produto (Seção 2.2, 2.3) são específicas e quantificáveis (ex: "Reduzir em 40% o tempo", "95% de precisão"), o que facilita a medição de sucesso.

*   **Potenciais Fraquezas e Desafios:**
    *   **Complexidade da "Mágica":** O sucesso do produto depende quase inteiramente da qualidade da Feature 4.1.1 (PLN). Se a tradução de linguagem natural para consultas de dados for imprecisa ou limitada, a confiança do usuário será erodida rapidamente, comprometendo todas as outras funcionalidades.
    *   **Ambição da Interatividade:** A Feature 4.2.3 (Interatividade) é fundamental para a retenção de usuários (especialmente Analistas), mas sua integração fluida em uma interface de chat é um desafio de UX e arquitetura notoriamente complexo. É aqui que reside seu problema principal.

### **2. Análise de Riscos e Pontos de Atenção**

Identifiquei os 5 principais riscos que podem comprometer o projeto:

1.  **Risco de Experiência do Usuário (UX) - (MUITO ALTO):** A transição entre a conversa (fluida, baseada em texto) e a visualização de dados (estruturada, gráfica) é o ponto de maior atrito. Se o usuário sentir que está "saindo" da conversa para ver um gráfico, a experiência se quebra. Este é o seu desafio atual e o maior risco para a adoção do produto.

2.  **Risco Técnico de Tradução (PLN -> Consulta) - (ALTO):** A capacidade do agente de converter perguntas ambíguas em consultas de dados precisas é o núcleo técnico do produto. Falhas aqui geram respostas incorretas, minando a confiança (meta de 95% de precisão). A complexidade aumenta com a necessidade de cruzar fontes de dados, como solicitado pela persona Ana.

3.  **Risco de Governança de Dados - (MÉDIO):** O agente é tão inteligente quanto o seu **Catálogo de Dados (Feature 4.3.2)**. Se os metadados não forem ricos, atualizados e bem gerenciados, o agente não terá o contexto de negócio necessário para desambiguar termos ("faturamento" significa bruto ou líquido?) ou entender relacionamentos.

4.  **Risco de Performance e Escalabilidade - (MÉDIO):** Os Requisitos Não-Funcionais (NFRs) são exigentes (consultas < 3s, dashboards < 10s, suportar +100% de dados). Uma arquitetura que não planeje para cache, otimização de consultas e escalonamento horizontal irá falhar em atender a esses NFRs à medida que a base de usuários e o volume de dados crescerem.

5.  **Risco de Gestão de Expectativas - (BAIXO/MÉDIO):** O termo "agente conversacional" pode levar os usuários a esperarem uma inteligência quase humana. O sistema precisa ser excelente em comunicar suas limitações e guiar o usuário para perguntas que ele consegue responder, evitando a frustração do "Desculpe, não entendi".

### **3. [SEÇÃO CRÍTICA] Estratégia de Implementação para Gráficos Conversacionais**

Esta seção detalha uma solução robusta para o seu principal desafio.

#### **3.1. Fluxo de Experiência do Usuário (UX Flow)**

O fluxo deve ser iterativo e colaborativo, fazendo o usuário sentir que está construindo a visualização *com* o agente.

1.  **Iniciação (Pergunta Ampla):**
    *   **Usuário:** "me mostre as vendas do último trimestre."

2.  **Desambiguação Guiada (O Agente Pede Esclarecimentos):**
    *   **Agente:** "Claro. Posso gerar um gráfico de vendas para o último trimestre. Para que a visualização seja mais útil, por favor, me ajude com alguns detalhes:"
        *   *Como você gostaria de ver as vendas?* (Oferece botões de sugestão) `[Por Região]`, `[Por Categoria de Produto]`, `[Evolução Mensal]`
        *   *Qual tipo de gráfico você prefere?* (Oferece botões de sugestão) `[Barras]`, `[Linhas]`, `[Pizza]`

3.  **Confirmação e Geração:**
    *   O usuário clica em `[Por Região]` e `[Barras]`.
    *   **Agente:** "Entendido. Gerando um gráfico de barras com as vendas por região do último trimestre."
    *   (O agente exibe uma prévia ou o gráfico diretamente na interface).

4.  **Apresentação e Interação Contínua:**
    *   O gráfico de barras interativo é renderizado **diretamente na área da conversa**.
    *   Abaixo do gráfico, o agente oferece **ações contextuais** como botões: `[Ver dados em tabela]`, `[Filtrar por estado]`, `[Adicionar ao meu dashboard]`, `[Exportar como PNG]`.

#### **3.2. Arquitetura Técnica para Geração de Gráficos**

A melhor abordagem é desacoplar a lógica de conversação da lógica de renderização de gráficos. O agente não deve criar uma imagem. Ele deve criar uma **especificação de gráfico**.

*   **Proposta:** **Backend (Agente) gera JSON para o Frontend (UI)**.
    1.  **Backend:** Após a desambiguação, o agente (LLM/PLN) traduz a solicitação do usuário em uma especificação de gráfico estruturada, como um **JSON compatível com Vega-Lite, Plotly ou Chart.js**. Este JSON contém:
        *   `chart_type`: "bar"
        *   `data_query`: A consulta SQL ou DSL para buscar os dados.
        *   `encoding`: { `x`: {"field": "regiao", "type": "nominal"}, `y`: {"field": "vendas_total", "type": "quantitative"} }
        *   `title`: "Vendas por Região (Último Trimestre)"
    2.  **Frontend:** A interface do chat recebe este JSON. Um componente React/Vue/Angular dedicado a gráficos usa uma biblioteca como **Plotly.js** ou **Vega-Embed** para renderizar o gráfico interativo a partir da especificação.

*   **Certificação de Implementação:**
    *   **Justificativa:** Esta arquitetura é superior porque separa as responsabilidades. O LLM foca no que faz de melhor (processar linguagem), enquanto a biblioteca de frontend foca no que faz de melhor (renderizar gráficos interativos e performáticos).
    *   **Trade-offs:**
        *   **Alternativa Descartada:** Gerar uma imagem estática (PNG com Matplotlib/Seaborn) no backend.
        *   **Prós da Alternativa:** Simplicidade inicial de implementação no backend.
        *   **Contras da Alternativa (e por que foi descartada):** Viola diretamente a **Feature 4.2.3 (Interatividade)**. É uma experiência "morta", não permite filtros ou exploração. Cada pequena alteração (ex: mudar de barras para linhas) exigiria uma nova consulta ao backend, violando o **NFR de Desempenho** (<3s).
    *   **Alinhamento com Requisitos:**
        *   **Feature 4.2.3 (Interatividade):** Atendido nativamente.
        *   **Desempenho:** A renderização no cliente é rápida, e interações como zoom ou tooltip não exigem novas chamadas de rede.
        *   **Escalabilidade:** O backend apenas envia um JSON leve, reduzindo a carga do servidor e a latência de rede.

#### **3.3. Modelo de Interação (Estático vs. Interativo)**

O modelo deve ser **interativo na conversa**.

*   **Proposta:** O gráfico deve ser um componente rico e explorável dentro do feed da conversa, não um link para um dashboard externo ou uma imagem estática. O usuário não deve sentir que está "saindo" do chat.

*   **Certificação de Implementação:**
    *   **Justificativa:** Manter o usuário no fluxo da conversa é crucial para a **Usabilidade (NFR)** e para a visão do produto de "tornar o processo tão simples quanto conversar". Um link externo quebra o fluxo e adiciona carga cognitiva.
    *   **Trade-offs:**
        *   **Alternativa Descartada:** Enviar um link para um dashboard completo.
        *   **Prós da Alternativa:** Reutiliza uma interface de dashboard já existente.
        *   **Contras da Alternativa (e por que foi descartada):** É uma solução preguiçosa que não resolve o problema central da integração conversacional. Para perguntas rápidas como a de Carlos ("ver um gráfico de barras"), ser forçado a abrir um dashboard completo é uma experiência ruim e desalinhada com a simplicidade prometida.
    *   **Alinhamento com Requisitos:**
        *   **Visão do Produto (2.1):** Mantém a interação com dados dentro da interface principal.
        *   **Usabilidade (NFR):** Reduz o número de cliques e mudanças de contexto para obter um insight.

#### **3.4. Tratamento de Ambiguidade e Desambiguação**

A estratégia deve ser proativa e baseada no Catálogo de Dados.

*   **Proposta:** Implementar uma camada de "Slot Filling" (Preenchimento de Lacunas) antes da geração da consulta.
    1.  **Análise da Intenção:** O agente identifica a intenção ("visualizar dados") e as entidades ("vendas", "último trimestre").
    2.  **Verificação de Lacunas:** O sistema consulta o **Catálogo de Dados (Feature 4.3.2)** para entender que a métrica "vendas" pode ser quebrada por dimensões como `região`, `produto`, `canal_de_venda`. Ele percebe que uma dimensão é necessária para um gráfico útil.
    3.  **Geração de Perguntas de Esclarecimento:** Com base nas dimensões disponíveis no catálogo para aquela métrica, o agente gera as perguntas de desambiguação e as apresenta como botões, como descrito no UX Flow.

*   **Certificação de Implementação:**
    *   **Justificativa:** Esta abordagem transforma o agente de um "adivinhador" em um "assistente colaborativo". Isso aumenta drasticamente a precisão das respostas e a confiança do usuário.
    *   **Trade-offs:**
        *   **Alternativa Descartada:** Tentar adivinhar a dimensão mais provável (ex: sempre agrupar por tempo).
        *   **Prós da Alternativa:** Menos um passo para o usuário.
        *   **Contras da Alternativa (e por que foi descartada):** Adivinhações erradas são extremamente frustrantes e levam o usuário a abandonar a ferramenta. O custo de uma pergunta de esclarecimento é muito menor que o custo de um gráfico inútil.
    *   **Alinhamento com Requisitos:**
        *   **Meta de Produto (2.3):** Essencial para atingir ">95% de precisão".
        *   **Feature 4.3.2 (Catálogo de Dados):** Torna o catálogo um componente ativo e central da arquitetura, não apenas um repositório passivo.

### **4. Recomendações Técnicas e de Arquitetura**

*   **Pilha de Tecnologia (Stack):**
    *   **Backend:** Python com FastAPI (pela performance e facilidade de uso para APIs) ou Node.js com TypeScript.
    *   **Frontend:** React ou Vue.js.
    *   **Bibliotecas de Gráfico:** **Plotly.js** é uma excelente escolha por seu suporte robusto a especificações JSON e interatividade nativa. Vega-Lite é uma alternativa poderosa e mais declarativa.
    *   **Cache:** Utilizar Redis para cachear tanto os resultados de consultas de dados quanto, potencialmente, as especificações de gráficos para perguntas recorrentes.

*   **Arquitetura de Serviços:**
    *   **Proposta:** Adotar uma arquitetura orientada a serviços desde o início, mesmo que não sejam microsserviços completos.
        1.  **Serviço de Interface (Frontend):** O aplicativo web Streamlit/React.
        2.  **Serviço de Orquestração (BFF - Backend for Frontend):** Recebe as requisições do chat, gerencia o estado da conversa e orquestra as chamadas para outros serviços.
        3.  **Serviço do Agente (PLN):** Responsável por interpretar o texto, gerenciar a desambiguação e gerar a especificação do gráfico/consulta.
        4.  **API de Dados:** Um serviço seguro que executa as consultas no banco de dados e aplica as regras de **RBAC (Feature 4.4.2)**, garantindo que um usuário só veja os dados que tem permissão.

*   **Certificação de Implementação:**
    *   **Justificativa:** Esta arquitetura desacoplada permite que cada componente escale de forma independente. Se a geração de PLN se tornar um gargalo, o **Serviço do Agente** pode ser escalado sem afetar o resto do sistema.
    *   **Alinhamento com Requisitos:**
        *   **Escalabilidade (NFR):** Atendido pela separação de preocupações.
        *   **Segurança (NFR):** A centralização do acesso a dados na **API de Dados** torna a implementação e auditoria do RBAC muito mais simples e segura.
        *   **Confiabilidade (NFR):** Falhas em um serviço (ex: o Agente) podem ser tratadas de forma mais graciosa sem derrubar todo o sistema.

### **5. Plano de Ação Sugerido (Roadmap Simplificado)**

**Fase 1: MVP - Validar o Core Loop (1-2 meses)**
*   **Foco:** Provar que o fluxo "Pergunta -> Resposta Correta" funciona para um escopo limitado.
*   **Features do PRD:**
    *   `4.1.1 (PLN)`: Focado em um subconjunto de perguntas (ex: apenas vendas e faturamento).
    *   `4.1.2 (Geração de Respostas)`: Gerar respostas de texto, números e **gráficos estáticos (PNG)** como uma primeira etapa para validar a lógica de dados.
    *   `4.4.1 (Autenticação)` e `4.4.2 (RBAC)`: Segurança é inegociável desde o início.
*   **Meta:** Permitir que a persona **Carlos (Diretor)** faça perguntas simples e receba um gráfico correto, mesmo que não interativo.

**Fase 2: Versão 1.0 - Lançamento com Experiência Interativa (Próximos 3-4 meses)**
*   **Foco:** Implementar a estratégia de gráficos conversacionais completa e enriquecer a experiência.
*   **Features do PRD:**
    *   Implementar a **arquitetura de especificação de gráfico (JSON)** e os **gráficos interativos (Feature 4.2.3)** no chat.
    *   Implementar a **estratégia de desambiguação** baseada no catálogo.
    *   `4.3.2 (Gerenciamento de Catálogo)`: Construir a interface para os Admins gerenciarem os metadados.
    *   `4.1.3 (Histórico de Conversas)`.
*   **Meta:** Atender plenamente às necessidades da persona **Ana (Analista)**, que precisa de exploração e interatividade.

**Fase 3: Pós-Lançamento - Escala e Otimização (Contínuo)**
*   **Foco:** Melhorar a inteligência do agente, a performance e a governança.
*   **Features do PRD:**
    *   `4.2.1 (Dashboard Principal)`: Permitir que os usuários "fixem" gráficos gerados na conversa em um dashboard pessoal.
    *   `4.3.1 (Monitoramento de Pipeline)`.
    *   `4.4.3 (Painel de Administração)`.
*   **Meta:** Atingir os NFRs de **Escalabilidade** e **Confiabilidade (99.9%)** e aumentar a **adoção (Meta 2.2)** em toda a organização.

---

Espero que este relatório forneça a clareza e a direção estratégica necessárias. Estou à disposição para discutir qualquer um desses pontos em maior profundidade.
[CÓDIGO-FONTE PARA ANÁLISE](INSTRUÇÃO: COLOQUE AQUI OS FICHEIROS DE CÓDIGO ATUAIS MAIS RELEVANTES PARA A REFATORAÇÃO)
Arquivo: core/agents/supervisor_agent.py (se ainda existir, para extrair a lógica)
# core/agents/supervisor_agent.py
import logging
from typing import List, Dict, Any # Import necessary types

from core.llm_base import BaseLLMAdapter
from core.agents.tool_agent import ToolAgent
from core.agents.code_gen_agent import CodeGenAgent

class SupervisorAgent:
    """
    Agente supervisor que roteia a consulta do usuário para o agente especialista apropriado.
    """
    def __init__(self, llm_adapter: BaseLLMAdapter):
        """
        Inicializa o supervisor, o ToolAgent, o CodeGenAgent e o LLM de roteamento.
        """
        self.logger = logging.getLogger(__name__)
        self.routing_llm = llm_adapter # Use o adaptador injetado
        self.tool_agent = ToolAgent(llm_adapter=llm_adapter)
        self.code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)
        self.logger.info("SupervisorAgent inicializado com os agentes especialistas.")

    def _build_routing_prompt(self, query: str) -> List[Dict[str, str]]:
        """
        Constrói o prompt para o LLM de roteamento decidir qual agente usar.
        Retorna uma lista de mensagens no formato esperado pela API do OpenAI.
        """
        system_message = {
            "role": "system",
            "content": "Você é um agente supervisor responsável por rotear consultas de usuários para o agente especialista correto."
        }
        user_message = {
            "role": "user",
            "content": f"""
            Você tem dois agentes especialistas disponíveis:
            1.  **ToolAgent**: Este agente usa um conjunto de ferramentas predefinidas para responder a perguntas simples sobre os dados, como procurar informações específicas (por exemplo, o preço de um produto) ou obter o esquema do banco de dados. É rápido e eficiente para consultas diretas.
            2.  **CodeGenAgent**: Este agente gera e executa código Python para responder a perguntas complexas que exigem análise de dados, agregações, cálculos ou visualizações (gráficos). É poderoso, mas mais lento.

            Sua tarefa é analisar a consulta do usuário e decidir qual agente é mais adequado.

            - Se a consulta for uma pergunta simples que pode ser respondida consultando informações diretas, encaminhe para o **ToolAgent**.
            - Se a consulta exigir análise complexa, cálculos, agregações ou a geração de um gráfico, encaminhe para o **CodeGenAgent**.

            Com base na consulta abaixo, qual agente deve ser usado? Responda com apenas uma palavra: "tool" ou "code".

            **Exemplos:**

            Consulta: "Qual o preço do produto 'Camisa Polo Azul'?"
            Resposta: tool

            Consulta: "Liste todas as categorias de produtos."
            Resposta: tool

            Consulta: "Qual a data da última venda do produto com ID 123?"
            Resposta: tool

            Consulta: "Mostre um gráfico de vendas por mês no último ano."
            Resposta: code

            Consulta: "Calcule a média de vendas por região."
            Resposta: code

            Consulta: "Qual o produto mais vendido no trimestre anterior e qual o seu faturamento total?"
            Resposta: code

            **Consulta do Usuário:** "{query}"
            """
        }
        return [system_message, user_message]

    def route_query(self, query: str) -> dict:
        """
        Analisa a consulta, roteia para o agente apropriado e retorna a resposta.
        """
        self.logger.info(f"Roteando a consulta: '{query}'")

        routing_messages = self._build_routing_prompt(query)
        
        # Call get_completion with messages and extract content
        llm_response = self.routing_llm.get_completion(messages=routing_messages)
        
        if "error" in llm_response:
            self.logger.error(f"Erro interno ao rotear a consulta: {llm_response['error']}")
            self.logger.warning("Não foi possível determinar o agente apropriado. Tentando com o ToolAgent.")
            return self.tool_agent.process_query(query)

        routing_decision = llm_response.get("content", "").strip().lower()

        self.logger.info(f"Decisão de roteamento: {routing_decision}")

        if "tool" in routing_decision:
            self.logger.info("Encaminhando para o ToolAgent.")
            return self.tool_agent.process_query(query)
        elif "code" in routing_decision:
            self.logger.info("Encaminhando para o CodeGenAgent.")
            return self.code_gen_agent.generate_and_execute_code(query)
        else:
            self.logger.warning(f"Decisão de roteamento inválida: '{routing_decision}'. Usando ToolAgent como padrão.")
            return self.tool_agent.process_query(query)
Arquivo: core/agents/caculinha_bi_agent.py (o placeholder atual)
import logging
import re
import json # Added import
import uuid # Added import
from typing import List, Dict, Any, Tuple
import pandas as pd
import os
from langchain_core.tools import tool
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, ToolCall
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from core.llm_langchain_adapter import CustomLangChainLLM

from core.connectivity.base import DatabaseAdapter
from core.config.settings import settings # Import the settings instance

logger = logging.getLogger(__name__)

def create_caculinha_bi_agent(
    parquet_dir: str,
    code_gen_agent: Any, # Use Any for now to avoid circular imports
    llm_adapter: Any # Add llm_adapter for tool selection
) -> Tuple[Runnable, List]:
    """
    Cria um agente de BI substituto e suas ferramentas, com o adaptador de banco de dados injetado.

    Args:
        db_adapter: Uma instância que segue a interface DatabaseAdapter.

    Returns:
        Uma tupla contendo o agente executável e a lista de suas ferramentas.
    """

    from core.tools.data_tools import query_product_data, list_table_columns

    @tool
    def generate_and_execute_python_code(query: str) -> Dict[str, Any]:
        """Gera e executa código Python para análises complexas e gráficos."""
        logger.info(f"Gerando e executando código Python para a consulta: {query}")
        return code_gen_agent.generate_and_execute_code(query)

    # A lista de ferramentas agora é definida dentro do escopo que tem acesso ao db_adapter
    bi_tools = [query_product_data, list_table_columns, generate_and_execute_python_code]

    # --- LLM para Geração de SQL ---
    sql_gen_llm = ChatOpenAI(
        model=settings.LLM_MODEL_NAME,
        openai_api_key=settings.OPENAI_API_KEY.get_secret_value(),
        temperature=0,
    )

    # Get parquet schema
    # This is a simplified way to get schema from parquet.
    # In a real scenario, you might have a metadata store for parquet files.
    parquet_schema = {}
    try:
        df_sample = pd.read_parquet(os.path.join(parquet_dir, "ADMAT_REBUILT.parquet"), columns=[])
        for col in df_sample.columns:
            parquet_schema[col] = str(df_sample[col].dtype)
    except Exception as e:
        logger.error(f"Erro ao inferir esquema do parquet: {e}")
        parquet_schema = {"error": "Não foi possível inferir o esquema do parquet."}
    
    schema_str = "\n".join([f"- {col}: {dtype}" for col, dtype in parquet_schema.items()]) # Convert schema to string for the prompt

    sql_gen_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Você é um assistente de BI. Sua tarefa é converter a consulta em linguagem natural do usuário em um objeto JSON que representa os filtros para consultar o arquivo ADMAT_REBUILT.parquet.
O arquivo está localizado em 'C:/Users/André/Documents/Agent_BI/data/parquet_cleaned/ADMAT_REBUILT.parquet'.

Use o seguinte esquema de dados (coluna: tipo) para gerar os filtros JSON:
{tables}

**IMPORTANTE: Para o código do produto, use a coluna 'CÓDIGO' (com acento e maiúsculas) conforme o schema do Parquet.**

Retorne APENAS o objeto JSON. Não inclua explicações ou qualquer outro texto.
O JSON deve ter a seguinte estrutura:
{{
    "target_file": "ADMAT_REBUILT.parquet",
    "filters": [
        {{"column": "nome_da_coluna", "operator": "operador", "value": "valor"}}
    ]
}}

Operadores suportados: "==", "!=", ">", "<", "contains".
Para buscas em colunas de texto (string), sempre use o operador "contains".
Para buscas em colunas numéricas, use "==", "!=", ">", "<".

Exemplo 1:
Consulta: Qual é o preço do produto 369947?
JSON:
```json
{{
    "target_file": "ADMAT_REBUILT.parquet",
    "filters": [
        {{"column": "CÓDIGO", "operator": "==", "value": 369947}}
    ]
}}
```

Exemplo 2:
Consulta: Liste todos os produtos da categoria 'Eletrônicos' com preço maior que 100.
JSON:
```json
{{
    "target_file": "ADMAT_REBUILT.parquet",
    "filters": [
        {{"column": "categoria", "operator": "contains", "value": "Eletrônicos"}},
        {{"column": "preco_38_percent", "operator": ">", "value": 100}}
    ]
}}
```

Exemplo 3:
Consulta: Mostre os produtos com vendas nos últimos 30 dias maiores que 50.
JSON:
```json
{{
    "target_file": "ADMAT_REBUILT.parquet",
    "filters": [
        {{"column": "VEND# QTD 30D", "operator": ">", "value": 50}}
    ]
}}
```


"""
            ),
            ("user", "{query}")
        ]
    )

    sql_generator_chain = sql_gen_prompt | sql_gen_llm

    def agent_runnable_logic(state: Dict[str, Any]) -> Dict[str, Any]:
        last_message = state["messages"][-1]

        if isinstance(last_message, HumanMessage):
            user_query = last_message.content
            logger.info(f"Agente de BI recebeu a consulta: {user_query}")

            # LLM para decisão de ferramenta
            tool_selection_llm = CustomLangChainLLM(llm_adapter=llm_adapter)

            tool_selection_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "Você é um assistente de BI. Sua tarefa é decidir qual ferramenta usar para responder à consulta do usuário. As ferramentas disponíveis são:\n" 
                        "- `query_product_data`: Para consultas que podem ser respondidas buscando dados específicos de produtos com filtros (ex: buscar preço de produto, listar produtos por categoria).\n" 
                        "- `list_table_columns`: Para listar todas as colunas de uma tabela (arquivo Parquet) específica.\n" 
                        "- `generate_and_execute_python_code`: Para análises complexas, cálculos, agregações ou geração de gráficos que exigem código Python.\n\n" 
                        "Retorne APENAS o nome da ferramenta: `query_product_data`, `list_table_columns` ou `generate_and_execute_python_code`.",
                    ),
                    ("user", "{query}"),
                ]
            )

            tool_selection_chain = tool_selection_prompt | tool_selection_llm
            
            # Decide qual ferramenta usar
            tool_decision_message = tool_selection_chain.invoke({"query": user_query})
            tool_decision = tool_decision_message.content.strip()
            logger.info(f"Decisão da ferramenta: {tool_decision}")

            if "query_product_data" in tool_decision:
                # Gerar JSON de filtros e retornar ToolCall
                generated_json_message = sql_generator_chain.invoke({"query": user_query, "tables": schema_str})
                generated_json_content = generated_json_message.content.strip()
                
                json_match = re.search(r"```json\n(.*?)```", generated_json_content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                else:
                    json_str = generated_json_content
                
                try:
                    parsed_json = json.loads(json_str)
                    target_file = parsed_json.get("target_file", "ADMAT_REBUILT.parquet")
                    filters = parsed_json.get("filters", [])
                    logger.info(f"JSON de filtros gerado: {parsed_json}")
                    
                    # Return AIMessage encapsulating ToolCall for query_product_data
                    return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="query_product_data", args={"target_file": target_file, "filters": filters})])]}
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON gerado: {e}. Conteúdo: {json_str}")
                    return {"messages": state["messages"] + [AIMessage(content=f"Desculpe, não consegui processar sua consulta devido a um erro na geração dos filtros: {e}")]}

            elif "list_table_columns" in tool_decision:
                table_name = "ADMAT_REBUILT" # This needs to be dynamically extracted in a real scenario
                logger.info(f"Listando colunas para a tabela: {table_name}")
                # Return AIMessage encapsulating ToolCall for list_table_columns
                return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="list_table_columns", args={"table_name": table_name})])]}

            elif "generate_and_execute_python_code" in tool_decision:
                # Return AIMessage encapsulating ToolCall for CodeGenAgent
                return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="generate_and_execute_python_code", args={"query": user_query})])]}
            else:
                return {"messages": [AIMessage(content="Desculpe, não consegui determinar a ferramenta apropriada para sua consulta.")]}

        elif isinstance(last_message, ToolMessage):
            # This path is taken after a tool has been executed by the ToolNode.
            # The agent needs to process the tool's output and generate an AIMessage.
            # The AIMessage generation is now handled by process_bi_tool_output_func in graph_builder.py
            return state
        else:
            # Handle other unexpected message types
            formatted_output = f"Erro: Tipo de mensagem inesperado no estado: {type(last_message)}"
            logger.error(formatted_output)
            return {"messages": state["messages"] + [AIMessage(content=formatted_output)]}

    # O runnable é a própria lógica do agente
    agent_runnable = RunnableLambda(agent_runnable_logic)

    return agent_runnable, bi_tools


Arquivo: core/graph/graph_builder.py (a versão atual)
import logging
from typing import Literal, Any
import json
import plotly.io as pio

from langchain_core.messages import AIMessage, ToolMessage, BaseMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from core.agent_state import AgentState
from core.agents.caculinha_bi_agent import create_caculinha_bi_agent
from core.agents.code_gen_agent import CodeGenAgent
from core.config.settings import Settings
from core.connectivity.base import DatabaseAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphBuilder:
    """Encapsula a lógica de construção do grafo LangGraph com injeção de dependência."""

    def __init__(self, settings: Settings, db_adapter: DatabaseAdapter, code_gen_agent: CodeGenAgent, llm_adapter: Any):
        """
        Inicializa o construtor do grafo com as dependências necessárias.
        """
        self.settings = settings
        self.db_adapter = db_adapter
        self.code_gen_agent = code_gen_agent
        self.llm_adapter = llm_adapter
        self.bi_agent_runnable, bi_tools = create_caculinha_bi_agent(self.settings.PARQUET_DIR, self.code_gen_agent, self.llm_adapter)
        self.bi_tool_node = ToolNode(bi_tools)

    def bi_agent_node_func(self, state: AgentState) -> dict:
        """Executa o agente de BI."""
        logger.info("--- Nó do Agente de BI ---")
        agent_output = self.bi_agent_runnable.invoke(state)
        return agent_output

    def process_bi_tool_output_func(self, state: AgentState) -> dict:
        """Processa a saída de uma ferramenta de BI e atualiza o estado."""
        logger.info("--- Nó de Processamento da Saída da Ferramenta de BI ---")
        last_msg = state["messages"][-1]

        if not isinstance(last_msg, ToolMessage):
            return {}

        content = last_msg.content
        tool_name = last_msg.name

        formatted_output = ""

        if tool_name == "generate_and_execute_python_code":
            processed_content = None
            if isinstance(content, str):
                try:
                    processed_content = json.loads(content)
                except json.JSONDecodeError:
                    formatted_output = f"Saída da ferramenta de geração de código não é um JSON válido: {content}"
            elif isinstance(content, dict):
                processed_content = content

            if processed_content and isinstance(processed_content, dict):
                content_type = processed_content.get("type")
                output = processed_content.get("output")

                if content_type == "chart":
                    formatted_output = "Gráfico gerado com sucesso e disponível para visualização."
                    try:
                        fig = pio.from_json(output)
                        return {"messages": [AIMessage(content=formatted_output, additional_kwargs={"plotly_fig": fig})]}
                    except Exception as e:
                        logger.error(f"Erro ao desserializar a figura Plotly: {e}")
                        formatted_output = "Erro ao processar o gráfico gerado."
                elif content_type == "dataframe":
                    formatted_output = "Dados processados e disponíveis."
                    return {"messages": [AIMessage(content=formatted_output)], "retrieved_data": output}
                else:
                    formatted_output = f"Saída da ferramenta de geração de código com tipo desconhecido: {processed_content}"
            elif not formatted_output:
                formatted_output = f"Saída da ferramenta de geração de código não pôde ser processada. Tipo: {type(content)}, Conteúdo: {content}"
        else:
            formatted_output = f"Saída de ferramenta desconhecida: {tool_name} - {content}"

        return {"messages": [AIMessage(content=formatted_output)]}

    def route_from_bi_agent(self, state: AgentState) -> Literal["bi_tools", "__end__"]:
        """Decide se deve chamar as ferramentas de BI ou finalizar."""
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and not last_message.tool_calls:
            return "__end__"
        elif isinstance(last_message, BaseMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "bi_tools"
        return "__end__"

    def build(self):
        """Constrói e compila o grafo de execução do LangGraph."""
        workflow = StateGraph(AgentState)

        workflow.add_node("caculinha_bi_agent", self.bi_agent_node_func)
        workflow.add_node("bi_tools", self.bi_tool_node)
        workflow.add_node("process_bi_tool_output", self.process_bi_tool_output_func)

        workflow.set_entry_point("caculinha_bi_agent")

        workflow.add_conditional_edges(
            "caculinha_bi_agent",
            self.route_from_bi_agent,
            {"bi_tools": "bi_tools", "__end__": END},
        )

        workflow.add_edge("bi_tools", "process_bi_tool_output")
        workflow.add_edge("process_bi_tool_output", END)

        app = workflow.compile()
        logger.info("Grafo LangGraph compilado com sucesso com uma arquitetura simplificada!")
        return app
Arquivo: main.py (a versão atual)
# core/main.py
import uvicorn
import logging
import subprocess
import sys
from datetime import timedelta

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Módulos locais
from core import schemas, security
from core.database import sql_server_auth_db as auth_db
from core.query_processor import QueryProcessor
from core.config.logging_config import setup_logging

# --- Configuração Inicial ---
setup_logging()

app = FastAPI(
    title="Agent_BI Backend",
    description="Serviço de backend para o Agente de BI, incluindo API de consulta e agendamento de tarefas.",
    version="2.0.0"
)

scheduler = AsyncIOScheduler()

# --- Lógica do Pipeline de Dados (Existente) ---
def get_db_credentials_from_file() -> dict:
    creds = {}
    try:
        with open("conexao.txt", "r") as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    creds[key.strip().lower()] = value.strip().strip("'")
    except FileNotFoundError:
        logging.warning("Arquivo conexao.txt não encontrado.")
    return creds

def trigger_pipeline_subprocess():
    logging.info("Acionando a execução do pipeline de dados via subprocesso...")
    creds = get_db_credentials_from_file()
    if not all(k in creds for k in ['server', 'database', 'user', 'password']):
        logging.error("Credenciais insuficientes para executar o pipeline.")
        return
    command = [sys.executable, "scripts/data_pipeline.py", "--server", creds['server'], "--database", creds['database'], "--user", creds['user'], "--password", creds['password']]
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        logging.info(f"Subprocesso do pipeline executado com sucesso: {process.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Subprocesso do pipeline falhou: {e.stderr}")

# --- Lógica de Autenticação e Dependências da API ---
def get_current_active_user(current_user: schemas.User = Depends(security.get_current_user)) -> schemas.User:
    # No futuro, esta função pode verificar se o usuário está desabilitado no banco de dados.
    # Por enquanto, a verificação está implícita no token.
    return current_user

# --- Endpoints da API ---
api_router = APIRouter(prefix="/api/v1")

@api_router.post("/auth/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    role, error_msg = auth_db.autenticar_usuario(form_data.username, form_data.password)
    if not role:
        logging.warning(f"Tentativa de login falha para o usuário {form_data.username}: {error_msg or 'Credenciais incorretas'}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_msg or "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": form_data.username, "role": role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/queries/", response_model=schemas.QueryResponse, tags=["Queries"])
async def handle_query(
    query: schemas.QueryRequest,
    current_user: schemas.User = Depends(get_current_active_user)
):
    try:
        # A inicialização do QueryProcessor pode precisar de mais contexto
        query_processor = QueryProcessor(user_id=current_user.username)
        # O método a ser chamado pode variar
        agent_response = await query_processor.process(query.text, query.session_id)
        return schemas.QueryResponse(**agent_response)
    except Exception as e:
        logging.error(f"Erro ao processar a consulta para o usuário {current_user.username}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a sua pergunta.")

@api_router.get("/users/me", response_model=schemas.User, tags=["Users"])
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

# --- Endpoints de Monitoramento e Ações (Existentes) ---
@app.get("/status", tags=["Monitoring"])
def read_root():
    return {"status": "Serviço de Backend do Agent_BI está no ar."}

@app.post("/run-pipeline", tags=["Actions"])
async def trigger_pipeline_endpoint():
    logging.info("Execução manual do pipeline de dados acionada via API.")
    scheduler.add_job(trigger_pipeline_subprocess, 'date', name="Execução Manual do Pipeline")
    return {"message": "Execução do pipeline de dados iniciada."}

# --- Inicialização ---
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    logging.info("Iniciando o agendador de tarefas do backend...")
    scheduler.add_job(
        trigger_pipeline_subprocess,
        trigger=CronTrigger(hour='8,20', minute='0'),
        id="data_pipeline_job",
        name="Pipeline de Extração de Dados SQL para Parquet",
        replace_existing=True
    )
    scheduler.start()
    logging.info("Agendador iniciado.")

@app.on_event("shutdown")
def shutdown_event():
    logging.info("Encerrando o agendador de tarefas...")
    scheduler.shutdown()
Arquivo: streamlit_app.py (a versão atual)
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import streamlit.components.v1 as components
import sys
import plotly.io as pio

from core import auth
from core.query_processor import QueryProcessor

audit_logger = logging.getLogger("audit")

# --- Constantes ---
from core.session_state import SESSION_STATE_KEYS
ROLES = {"ASSISTANT": "assistant", "USER": "user"}
PAGE_CONFIG = {
    "page_title": "Assistente de BI - Caçula",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# --- Configuração da Página e Estilos ---
st.set_page_config(**PAGE_CONFIG)

# Load CSS from external file for better organization
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def initialize_session_state():
    """Inicializa o estado da sessão se não existir."""
    if SESSION_STATE_KEYS["QUERY_PROCESSOR"] not in st.session_state:
        st.session_state[SESSION_STATE_KEYS["QUERY_PROCESSOR"]] = QueryProcessor()
    if SESSION_STATE_KEYS["MESSAGES"] not in st.session_state:
        st.session_state[SESSION_STATE_KEYS["MESSAGES"]] = [
            {
                "role": ROLES["ASSISTANT"],
                "output": "Olá! Como posso ajudar você hoje?",
            }
        ]
    if "dashboard_charts" not in st.session_state: # Adicionado para inicializar o dashboard_charts
        st.session_state.dashboard_charts = []


def handle_logout():
    """Limpa o estado da sessão e força o rerun para a tela de login."""
    username = st.session_state.get(SESSION_STATE_KEYS["USERNAME"], "N/A")
    audit_logger.info(f"Usuário {username} deslogado.")
    keys_to_clear = [
        SESSION_STATE_KEYS["AUTHENTICATED"],
        SESSION_STATE_KEYS["USERNAME"],
        SESSION_STATE_KEYS["ROLE"],
        SESSION_STATE_KEYS["LAST_LOGIN"],
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def show_bi_assistant():
    """Exibe a interface principal do assistente de BI."""
    st.markdown(
        "<h1 class='main-header'>📊 Assistente de BI Caçulinha</h1>",
        unsafe_allow_html=True,
    )
    
    

    # Exibir histórico de mensagens
    for idx, message in enumerate(st.session_state[SESSION_STATE_KEYS["MESSAGES"]]):
        with st.chat_message(message["role"]):
            output = message.get("output")
            if isinstance(output, pd.DataFrame):
                st.dataframe(output, use_container_width=True)
            elif isinstance(output, dict) and output.get("type") == "chart": # Para gráficos Plotly
                st.plotly_chart(output.get("output"), use_container_width=True, key=f"history_chart_{idx}")
            else: # Para texto, gráficos Plotly diretos ou outros tipos de dicionário inesperados
                if isinstance(output, go.Figure): # Se for um objeto Plotly Figure
                    st.plotly_chart(output, use_container_width=True, key=f"history_fig_{idx}")
                elif isinstance(output, str):
                    # Fallback: tentar decodificar JSON de Plotly se for uma string
                    fig = None
                    try:
                        if output.strip().startswith("{"):
                            fig = pio.from_json(output)
                    except Exception:
                        fig = None
                    if fig is not None:
                        st.plotly_chart(fig, use_container_width=True, key=f"history_json_fig_{idx}")
                    else:
                        st.markdown(str(output or ""))
                else: # Para texto ou outros tipos de dicionário inesperados
                    st.markdown(str(output or ""))

    # Exemplos de perguntas na barra lateral
    st.sidebar.markdown("### Exemplos de Perguntas:")
    st.sidebar.info("Qual o preço do produto 719445?")
    st.sidebar.info("Liste os produtos da categoria 'BRINQUEDOS'")
    st.sidebar.info("Mostre um gráfico de vendas para o produto 610403")

    # Entrada do usuário
    if prompt := st.chat_input("Faça uma pergunta sobre seus dados..."):
        # Input validation and sanitization
        if not prompt.strip(): # Check for empty or whitespace-only input
            st.warning("Por favor, digite uma pergunta válida.")
            return # Stop processing if input is empty

        if len(prompt) > 500: # Example: Limit input length to 500 characters
            st.warning("Sua pergunta é muito longa. Por favor, seja mais conciso (máximo 500 caracteres).")
            return # Stop processing if input is too long

        # Adicionar mensagem do usuário ao histórico e exibir
        st.session_state[SESSION_STATE_KEYS["MESSAGES"]].append(
            {"role": ROLES["USER"], "output": prompt}
        )
        with st.chat_message(ROLES["USER"]):
            st.markdown(prompt)

        # Processar a pergunta e obter a resposta
        with st.chat_message(ROLES["ASSISTANT"]):
            st.info("Aguarde enquanto o assistente processa sua solicitação...") # Added info message
            with st.spinner("O assistente de BI está pensando..."): # More generic spinner message
                query_processor = st.session_state[
                    SESSION_STATE_KEYS["QUERY_PROCESSOR"]
                ]
                response = query_processor.process_query(prompt)

                # Normaliza a resposta para exibição e histórico
                assistant_message = None
                if response.get("type") == "dataframe":
                    df = response.get("output")
                    st.dataframe(df, use_container_width=True)
                    assistant_message = {"role": ROLES["ASSISTANT"], "output": df}
                elif response.get("type") == "chart":
                    raw = response.get("output")
                    fig = None
                    try:
                        if isinstance(raw, str):
                            # Reconstrói a figura a partir de JSON serializado
                            fig = pio.from_json(raw)
                        elif isinstance(raw, dict) and raw.get("data") is not None:
                            # Constrói figura a partir de dicionário
                            fig = go.Figure(raw)
                        elif isinstance(raw, go.Figure):
                            fig = raw
                    except Exception as e:
                        st.error(f"Falha ao decodificar gráfico: {e}")

                    if fig is not None:
                        st.plotly_chart(fig, use_container_width=True, key=f"new_chart_{datetime.now().timestamp()}")

                        # Adicionar ao dashboard_charts
                        if "dashboard_charts" not in st.session_state:
                            st.session_state.dashboard_charts = []

                        st.session_state.dashboard_charts.append({
                            "type": "chart", # Tipo é 'chart'
                            "output": fig, # Objeto Plotly direto
                            "title": f"Gráfico gerado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", # Título genérico
                            "query": prompt, # A consulta original
                            "timestamp": datetime.now().timestamp()
                        })
                        st.success("Gráfico adicionado ao Dashboard!")

                        assistant_message = {"role": ROLES["ASSISTANT"], "output": {"type": "chart", "output": fig}}
                    else:
                        st.warning("Não foi possível renderizar o gráfico retornado.")
                        assistant_message = {"role": ROLES["ASSISTANT"], "output": str(response)}
                else:
                    text = response.get("output")
                    st.markdown(text if text is not None else "")
                    assistant_message = {"role": ROLES["ASSISTANT"], "output": text if text is not None else ""}

                # Adiciona a mensagem do assistente ao histórico já normalizada
                st.session_state[SESSION_STATE_KEYS["MESSAGES"]].append(assistant_message)

    st.markdown(
        f"<div class='footer'>Desenvolvido para Análise de Dados Caçula © {datetime.now().year}</div>",
        unsafe_allow_html=True,
    )


def show_admin_dashboard():
    """Exibe o painel de administração para usuários com perfil 'admin'."""
    st.markdown(
        "<h1 class='main-header'>⚙️ Painel de Administração</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='sub-header'>Gerencie usuários, configurações e monitore o sistema.</p>",
        unsafe_allow_html=True,
    )
    st.subheader("Funcionalidades:")
    st.write("- Gerenciamento de usuários")
    st.write("- Visualização de logs")
    st.write("- Configurações do sistema")
    st.markdown(
        f"<div class='footer'>Desenvolvido para Análise de Dados Caçula © {datetime.now().year}</div>",
        unsafe_allow_html=True,
    )


import logging
import uuid
# import sentry_sdk
import os
from core.config.logging_config import setup_logging
from core.utils.context import correlation_id_var

logger = logging.getLogger(__name__)

def main():
    """Função principal que controla o fluxo da aplicação."""
    setup_logging()
    # sentry_dsn = os.getenv("SENTRY_DSN")
    # if sentry_dsn:
    #     sentry_sdk.init(
    #         dsn=sentry_dsn,
    #         traces_sample_rate=1.0,
    #     )

    # Set correlation id
    if 'correlation_id' not in st.session_state:
        st.session_state.correlation_id = str(uuid.uuid4())
    correlation_id_var.set(st.session_state.correlation_id)

    logger.info("Iniciando a aplicação Streamlit.")
    initialize_session_state()

    # --- Verificação de Autenticação e Sessão ---
    if not st.session_state.get(SESSION_STATE_KEYS["AUTHENTICATED"]):
        auth.login()
        st.stop()

    if auth.sessao_expirada():
        st.warning(
            "Sua sessão expirou por inatividade. Faça login novamente para continuar."
        )
        handle_logout()
        # A tela de login será exibida no próximo rerun após o st.stop()
        st.stop()


    # --- Barra Lateral e Logout ---
    username = st.session_state.get(SESSION_STATE_KEYS["USERNAME"])
    role = st.session_state.get(SESSION_STATE_KEYS["ROLE"])

    

    if username:
        st.sidebar.markdown(
            f"<span style='color:#2563EB;'>Bem-vindo, <b>{username}</b>!</span>",
            unsafe_allow_html=True,
        )
        st.sidebar.markdown("<hr>", unsafe_allow_html=True)
        if st.sidebar.button("Sair"):
            handle_logout()

    # --- Renderização do Conteúdo Principal ---
    show_bi_assistant()


if __name__ == "__main__":
    main()