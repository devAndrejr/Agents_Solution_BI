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
