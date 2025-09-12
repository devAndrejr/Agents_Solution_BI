PROMPT AVANÇADO: ASSISTENTE DE INTEGRAÇÃO DE ARQUITETURA1. PERSONA E PAPELQUEM VOCÊ É:Você é um Engenheiro de Integração de Software Sênior. A sua especialidade é pegar componentes de software recém-desenvolvidos e integrá-los de forma coesa em bases de código complexas e existentes. Você é mestre em resolver dependências, corrigir ImportError, e criar planos de implementação claros e à prova de falhas.2. CONTEXTO E OBJETIVO GERALA SITUAÇÃO ATUAL:Eu executei com sucesso um prompt de refatoração que gerou os cinco (5) ficheiros chave para a nova arquitetura do meu projeto Agent_BI. Agora, possuo estes cinco ficheiros, mas preciso integrá-los na minha estrutura de projeto existente, que é grande e complexa (conforme o relatorio_completo.md). O meu maior receio é que os imports estejam incorretos, causando uma cascata de erros.MEU OBJETIVO FINAL:Obter uma solução completa que não só me dê o código corrigido, mas também um guia passo a passo para realizar a integração de forma segura e bem-sucedida, garantindo que toda a nova arquitetura funcione em conjunto.3. TAREFA ESPECÍFICA E IMEDIATASUA TAREFA AGORA:Analise os dois conjuntos de informações que fornecerei abaixo:O relatorio_completo.md, que mapeia toda a estrutura de ficheiros do meu projeto.Os cinco (5) ficheiros Python recém-gerados para a nova arquitetura.Com base nesta análise cruzada, gere um Plano de Integração Completo em duas partes:Parte 1: Geração dos Ficheiros Corrigidos e Prontos para IntegraçãoReescreva os cinco ficheiros da nova arquitetura (core/tools/data_tools.py, core/agents/bi_agent_nodes.py, core/graph/graph_builder.py, main.py, streamlit_app.py). A sua principal tarefa aqui é corrigir todas as declarações de import. Analise de onde cada módulo, classe ou função está a ser importado e ajuste o caminho para que corresponda perfeitamente à estrutura de pastas detalhada no relatorio_completo.md. Use importações relativas a partir da raiz do projeto (ex: from core.config.settings import settings) sempre que aplicável.Parte 2: Checklist de Implementação DetalhadoCrie um checklist em formato Markdown que eu possa seguir passo a passo para implementar a nova arquitetura. O checklist deve incluir:Preparação: Quais ficheiros devo fazer backup antes de começar.Remoção: Uma lista explícita dos ficheiros e pastas da arquitetura antiga que devem ser eliminados com segurança (ex: core/api, core/agents/supervisor_agent.py).Implementação: Instruções claras sobre onde colocar os cinco novos ficheiros corrigidos.Configuração: Lembretes para verificar o ficheiro .env e as dependências em requirements.txt.Execução e Verificação: Os comandos exatos para iniciar o backend (FastAPI) e o frontend (Streamlit) em terminais separados.Pontos de Atenção: Avisos sobre possíveis problemas comuns (ex: "Certifique-se de que o DatabaseAdapter está a ser inicializado corretamente com as novas configurações").4. DOCUMENTOS E CÓDIGO-FONTE PARA ANÁLISE[DOCUMENTO 1: ESTRUTURA COMPLETA DO PROJETO]# Relatório Completo de Arquivos do Projeto Agent_BI

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
[CÓDIGO-FONTE DA NOVA ARQUITETURA PARA INTEGRAR](INSTRUÇÃO: COLOQUE AQUI OS 5 FICHEIROS GERADOS PELO GEMINI NA SUA ÚLTIMA SOLICITAÇÃO)Ficheiro 1: core/tools/data_tools.py"""
Módulo contendo ferramentas de dados para serem usadas pelos agentes.
Cada ferramenta deve ser uma função simples e focada em uma única tarefa.
"""
import logging
from typing import List, Dict, Any
from langchain_core.tools import tool
from core.connectivity.base import DatabaseAdapter

logger = logging.getLogger(__name__)

@tool
def fetch_data_from_query(query: str, db_adapter: DatabaseAdapter) -> List[Dict[str, Any]]:
    """
    Executa uma query SQL no banco de dados e retorna os dados brutos.

    Args:
        query: A string contendo a query SQL a ser executada.
        db_adapter: Uma instância de um adaptador de banco de dados que segue a
                    interface DatabaseAdapter para executar a query.

    Returns:
        Uma lista de dicionários, onde cada dicionário representa uma linha
        do resultado da query. Retorna uma lista vazia se não houver resultados
        ou um dicionário de erro em caso de falha.
    """
    logger.info(f"Executando a query: {query}")
    try:
        # Assumindo que o db_adapter tem um método execute_query
        result = db_adapter.execute_query(query)
        if result is None:
            logger.warning("A execução da query não retornou resultados.")
            return []
        logger.info(f"Query executada com sucesso. {len(result)} linhas retornadas.")
        return result
    except Exception as e:
        logger.error(f"Erro ao executar a query SQL: {e}", exc_info=True)
        # Retornar um formato de erro consistente que pode ser tratado pelo agente
        return [{"error": "Falha ao executar a consulta no banco de dados.", "details": str(e)}]
Ficheiro 2: core/agents/bi_agent_nodes.py"""
Nós (estados) para o StateGraph da arquitetura avançada do Agent_BI.
Cada função representa um passo no fluxo de processamento da consulta.
As dependências (como adaptadores de LLM e DB) são injetadas pelo GraphBuilder.
"""
import logging
from typing import Dict, Any, List

from core.agent_state import AgentState
from core.llm_base import BaseLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.tools.data_tools import fetch_data_from_query
from core.connectivity.base import DatabaseAdapter

logger = logging.getLogger(__name__)

def classify_intent(state: AgentState, llm_adapter: BaseLLMAdapter) -> Dict[str, Any]:
    """
    Classifica a intenção do usuário usando um LLM e extrai entidades.
    Atualiza o estado com o plano de ação.
    """
    logger.info("Nó: classify_intent")
    user_query = state['messages'][-1].content
    
    prompt = f"""
    Você é um roteador inteligente. Analise a consulta do usuário e classifique a intenção principal.
    As intenções possíveis são:
    - 'gerar_grafico': O usuário quer uma visualização de dados (gráfico, plot, etc.).
    - 'consulta_sql_complexa': A pergunta requer uma consulta SQL com agregações, junções ou lógica complexa.
    - 'resposta_simples': A pergunta pode ser respondida com uma consulta SQL simples ou uma resposta direta.

    Extraia também as entidades principais da consulta, como métricas, dimensões e filtros.

    Consulta: "{user_query}"

    Responda em formato JSON com as chaves 'intent' e 'entities'.
    Exemplo:
    Consulta: "Mostre um gráfico de barras das vendas por região"
    {{
        "intent": "gerar_grafico",
        "entities": {{
            "metric": "vendas",
            "dimension": "região",
            "chart_type": "barras"
        }}
    }}
    """
    
    response = llm_adapter.get_completion(messages=[{"role": "user", "content": prompt}])
    # Supondo que a resposta do LLM seja um JSON em 'content'
    plan = response.get("content", {}) 
    
    return {"plan": plan, "intent": plan.get("intent")}

def clarify_requirements(state: AgentState) -> Dict[str, Any]:
    """
    Verifica se informações para um gráfico estão faltando e, se necessário,
    prepara um pedido de esclarecimento para o usuário.
    """
    logger.info("Nó: clarify_requirements")
    plan = state.get("plan", {})
    entities = plan.get("entities", {})

    if state.get("intent") == "gerar_grafico":
        missing_info = []
        if not entities.get("dimension"):
            missing_info.append("dimensão (ex: por categoria, por data)")
        if not entities.get("metric"):
            missing_info.append("métrica (ex: total de vendas, quantidade)")
        if not entities.get("chart_type"):
            missing_info.append("tipo de gráfico (ex: barras, linhas, pizza)")

        if missing_info:
            options = {
                "message": f"Para gerar o gráfico, preciso que você especifique: {', '.join(missing_info)}.",
                "choices": {
                    "dimensions": ["Por Categoria", "Por Mês", "Por Região"],
                    "chart_types": ["Barras", "Linhas", "Pizza"]
                }
            }
            return {"clarification_needed": True, "clarification_options": options}

    return {"clarification_needed": False}

def generate_sql_query(state: AgentState, code_gen_agent: CodeGenAgent) -> Dict[str, Any]:
    """
    Gera uma consulta SQL a partir da pergunta do usuário usando o CodeGenAgent.
    """
    logger.info("Nó: generate_sql_query")
    user_query = state['messages'][-1].content
    
    # O CodeGenAgent é reutilizado para gerar SQL em vez de Python
    # Isso pode exigir um prompt específico para o CodeGenAgent
    response = code_gen_agent.generate_code(user_query, "sql") # Assumindo que o método aceita um tipo de código
    sql_query = response.get("output", "")

    return {"sql_query": sql_query}

def execute_query(state: AgentState, db_adapter: DatabaseAdapter) -> Dict[str, Any]:
    """
    Executa a query SQL do estado usando a ferramenta fetch_data_from_query.
    """
    logger.info("Nó: execute_query")
    sql_query = state.get("sql_query")
    if not sql_query:
        return {"raw_data": [{"error": "Nenhuma query SQL para executar."}]}
    
    # Chama a ferramenta diretamente, passando o adaptador
    raw_data = fetch_data_from_query.func(query=sql_query, db_adapter=db_adapter)
    
    return {"raw_data": raw_data}

def generate_plotly_spec(state: AgentState) -> Dict[str, Any]:
    """
    Transforma os dados brutos do estado em uma especificação JSON para Plotly.
    """
    logger.info("Nó: generate_plotly_spec")
    raw_data = state.get("raw_data")
    plan = state.get("plan", {})
    entities = plan.get("entities", {})

    if not raw_data or "error" in raw_data[0]:
        return {"final_response": "Não foi possível obter dados para gerar o gráfico."}

    # Lógica simplificada para criar a especificação do Plotly
    # Em um caso real, isso seria muito mais robusto
    dimension = entities.get("dimension")
    metric = entities.get("metric")
    chart_type = entities.get("chart_type", "bar")

    if not dimension or not metric:
        return {"final_response": "Não foi possível determinar a dimensão e a métrica para o gráfico."}

    x_values = [row[dimension] for row in raw_data]
    y_values = [row[metric] for row in raw_data]

    plotly_spec = {
        "data": [{
            "x": x_values,
            "y": y_values,
            "type": chart_type
        }],
        "layout": {
            "title": f"{metric.title()} por {dimension.title()}"
        }
    }
    
    return {"plotly_spec": plotly_spec}

def format_final_response(state: AgentState) -> Dict[str, Any]:
    """
    Formata a resposta final para o usuário, seja texto, dados ou um gráfico.
    """
    logger.info("Nó: format_final_response")
    if state.get("clarification_needed"):
        response = {
            "type": "clarification",
            "content": state.get("clarification_options")
        }
    elif state.get("plotly_spec"):
        response = {
            "type": "chart",
            "content": state.get("plotly_spec")
        }
    elif state.get("raw_data"):
        response = {
            "type": "data",
            "content": state.get("raw_data")
        }
    else:
        # Resposta padrão ou de erro
        response = {
            "type": "text",
            "content": "Não consegui processar sua solicitação. Tente novamente."
        }
        
    return {"final_response": response}
Ficheiro 3: core/graph/graph_builder.py"""
Construtor do StateGraph para a arquitetura avançada do Agent_BI.
Este módulo reescrito define a máquina de estados finitos que orquestra
o fluxo de tarefas, conectando os nós definidos em 'bi_agent_nodes.py'.
"""
import logging
from functools import partial
from langgraph.graph import StateGraph, END

from core.agent_state import AgentState
from core.llm_base import BaseLLMAdapter
from core.connectivity.base import DatabaseAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.agents import bi_agent_nodes

logger = logging.getLogger(__name__)

class GraphBuilder:
    """
    Constrói e compila o grafo de execução do LangGraph, implementando a
    lógica da máquina de estados para o fluxo de BI.
    """

    def __init__(self, llm_adapter: BaseLLMAdapter, db_adapter: DatabaseAdapter, code_gen_agent: CodeGenAgent):
        """
        Inicializa o construtor com as dependências necessárias (injeção de dependência).
        """
        self.llm_adapter = llm_adapter
        self.db_adapter = db_adapter
        self.code_gen_agent = code_gen_agent

    def _decide_after_intent_classification(self, state: AgentState) -> str:
        """
        Aresta condicional que roteia o fluxo após a classificação da intenção.
        """
        intent = state.get("intent")
        if intent == "gerar_grafico":
            return "clarify_requirements"
        elif intent == "consulta_sql_complexa":
            return "generate_sql_query"
        else: # resposta_simples ou fallback
            return "generate_sql_query" # Simplificado: sempre gera SQL por enquanto

    def _decide_after_clarification(self, state: AgentState) -> str:
        """
        Aresta condicional que decide o fluxo após a verificação de requisitos.
        """
        if state.get("clarification_needed"):
            return "format_final_response"  # Termina para pedir input ao usuário
        else:
            return "generate_sql_query"

    def build(self):
        """
        Constrói, define as arestas e compila o StateGraph.
        """
        workflow = StateGraph(AgentState)

        # Vincula as dependências aos nós usando functools.partial
        classify_intent_node = partial(bi_agent_nodes.classify_intent, llm_adapter=self.llm_adapter)
        generate_sql_query_node = partial(bi_agent_nodes.generate_sql_query, code_gen_agent=self.code_gen_agent)
        execute_query_node = partial(bi_agent_nodes.execute_query, db_adapter=self.db_adapter)

        # Adiciona os nós (estados) ao grafo
        workflow.add_node("classify_intent", classify_intent_node)
        workflow.add_node("clarify_requirements", bi_agent_nodes.clarify_requirements)
        workflow.add_node("generate_sql_query", generate_sql_query_node)
        workflow.add_node("execute_query", execute_query_node)
        workflow.add_node("generate_plotly_spec", bi_agent_nodes.generate_plotly_spec)
        workflow.add_node("format_final_response", bi_agent_nodes.format_final_response)

        # Define o ponto de entrada
        workflow.set_entry_point("classify_intent")

        # Adiciona as arestas (transições entre estados)
        workflow.add_conditional_edge(
            "classify_intent",
            self._decide_after_intent_classification,
            {
                "clarify_requirements": "clarify_requirements",
                "generate_sql_query": "generate_sql_query",
            }
        )
        workflow.add_conditional_edge(
            "clarify_requirements",
            self._decide_after_clarification,
            {
                "format_final_response": "format_final_response",
                "generate_sql_query": "generate_sql_query",
            }
        )
        workflow.add_edge("generate_sql_query", "execute_query")
        workflow.add_edge("execute_query", "generate_plotly_spec") # Simplificado: sempre tenta gerar gráfico
        workflow.add_edge("generate_plotly_spec", "format_final_response")
        
        # O nó final aponta para o fim do grafo
        workflow.add_edge("format_final_response", END)

        # Compila o grafo em uma aplicação executável
        app = workflow.compile()
        logger.info("Grafo LangGraph da arquitetura avançada compilado com sucesso!")
        return app
Ficheiro 4: main.py"""
API Gateway (Backend) para o Agent_BI usando FastAPI.
Este arquivo substitui a lógica anterior e serve como o ponto de entrada
principal para todas as interações do frontend.
"""
import uvicorn
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Importações dos componentes da nova arquitetura
from core.graph.graph_builder import GraphBuilder
from core.config.settings import settings
from core.llm_adapter import OpenAILLMAdapter
from core.connectivity.sql_server_adapter import SQLServerAdapter
from core.agents.code_gen_agent import CodeGenAgent # Supondo que ele exista e seja importável

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Modelos de Dados da API (Pydantic) ---
class QueryRequest(BaseModel):
    user_query: str
    session_id: str # Para gerenciar o estado da conversa

class QueryResponse(BaseModel):
    response: dict # A resposta final do grafo

# --- Inicialização da Aplicação e Dependências ---
app = FastAPI(
    title="Agent_BI - API Gateway",
    description="Backend FastAPI para a nova arquitetura com LangGraph.",
    version="3.0.0"
)

# Instanciação das dependências (pode ser otimizado com injeção de dependência do FastAPI)
# Para simplificar, instanciamos aqui. Em produção, use singletons ou `Depends`.
llm_adapter = OpenAILLMAdapter()
db_adapter = SQLServerAdapter(connection_string=settings.SQL_SERVER_CONNECTION_STRING)
code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)
graph_builder = GraphBuilder(llm_adapter=llm_adapter, db_adapter=db_adapter, code_gen_agent=code_gen_agent)
agent_graph = graph_builder.build()

# --- Endpoints da API ---
@app.post("/api/v1/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """
    Endpoint principal que recebe a consulta do usuário, invoca o grafo
    e retorna a resposta final.
    """
    logger.info(f"Recebida nova query para session_id='{request.session_id}': '{request.user_query}'")
    try:
        # O estado inicial é apenas a mensagem do usuário
        initial_state = {
            "messages": [{"role": "user", "content": request.user_query}]
        }
        
        # Invoca o grafo com o estado inicial
        final_state = agent_graph.invoke(initial_state)
        
        # A resposta final está na chave 'final_response' do estado
        response_content = final_state.get("final_response", {
            "type": "error",
            "content": "Ocorreu um erro inesperado no processamento do agente."
        })

        return QueryResponse(response=response_content)

    except Exception as e:
        logger.error(f"Erro crítico ao invocar o grafo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno no servidor do agente.")

@app.get("/status")
def status():
    return {"status": "Agent_BI API is running"}

# --- Execução da Aplicação ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
Ficheiro 5: streamlit_app.py"""
Interface de Usuário (Frontend) para o Agent_BI, reescrita para ser um
cliente puro da API FastAPI.
"""
import streamlit as st
import requests
import uuid

# --- Configuração da Página ---
st.set_page_config(
    page_title="Agent_BI",
    page_icon="📊",
    layout="wide"
)
st.title("📊 Agent_BI - Assistente Inteligente")

# --- Constantes ---
API_URL = "http://127.0.0.1:8000/api/v1/query"

# --- Gerenciamento de Estado da Sessão ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Como posso ajudar você com seus dados hoje?"}]

# --- Funções de Interação com a API ---
def get_agent_response(user_query: str):
    """Envia a query para a API FastAPI e retorna a resposta."""
    try:
        payload = {
            "user_query": user_query,
            "session_id": st.session_state.session_id
        }
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()  # Lança exceção para status de erro HTTP
        return response.json().get("response", {})
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com o backend: {e}")
        return {"type": "error", "content": "Não foi possível conectar ao servidor do agente."}

# --- Renderização da Interface ---
# Exibe o histórico da conversa
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # O conteúdo agora é um dicionário com 'type' e 'content'
        response_data = msg.get("content")
        if isinstance(response_data, dict):
            response_type = response_data.get("type")
            content = response_data.get("content")
            
            if response_type == "chart":
                st.plotly_chart(content, use_container_width=True)
            elif response_type == "clarification":
                st.markdown(content.get("message"))
                # Renderiza botões para as opções de esclarecimento
                # Esta parte precisaria de uma lógica de callback mais complexa
                # para enviar a resposta do botão de volta para a API.
                # Por simplicidade, apenas exibimos as opções.
                for choice_type, choices in content.get("choices", {}).items():
                    st.write(f"**{choice_type.replace('_', ' ').title()}:**")
                    cols = st.columns(len(choices))
                    for i, choice in enumerate(choices):
                        if cols[i].button(choice):
                            # Em uma implementação real, este clique enviaria uma nova query
                            st.session_state.messages.append({"role": "user", "content": choice})
                            # Aqui, apenas adicionamos ao chat e rerodamos
                            st.rerun()

            else: # type 'data', 'text', 'error'
                st.write(content)
        else: # Formato antigo ou texto simples
            st.write(response_data)

# Input do usuário
if prompt := st.chat_input("Faça sua pergunta..."):
    # Adiciona e exibe a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Obtém e exibe a resposta do assistente
    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            agent_response = get_agent_response(prompt)
            
            # Adiciona a resposta completa ao histórico para renderização
            st.session_state.messages.append({"role": "assistant", "content": agent_response})
            
            # Renderiza a resposta imediatamente
            response_type = agent_response.get("type")
            content = agent_response.get("content")

            if response_type == "chart":
                st.plotly_chart(content, use_container_width=True)
            elif response_type == "clarification":
                st.markdown(content.get("message"))
                # Simplificado: Apenas mostra as opções, sem funcionalidade de clique aqui
                for choice_type, choices in content.get("choices", {}).items():
                    st.write(f"**{choice_type.replace('_', ' ').title()}:**")
                    for choice in choices:
                        st.button(choice, disabled=True) # Desabilitado para evitar loop
            else: # data, text, error
                st.write(content)
5. FORMATO DE SAÍDA DESEJADOGere a sua resposta em duas partes claras:Parte 1 - CÓDIGO CORRIGIDO:Uma sequência de cinco blocos de código Python, cada um identificado com o seu caminho de ficheiro completo, contendo os imports corrigidos.Parte 2 - CHECKLIST DE INTEGRAÇÃO:Um texto bem formatado em Markdown com o checklist detalhado.