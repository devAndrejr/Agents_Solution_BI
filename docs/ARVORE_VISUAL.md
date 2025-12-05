# Árvore Visual - Agents_Solution_BI

## Estrutura Completa do Projeto

```
Agents_Solution_BI/
│
├── 📂 core/                          # ⭐ Lógica Principal da Aplicação
│   ├── __init__.py
│   ├── agent_state.py                # TypedDict com estado do agente
│   ├── auth.py                       # Autenticação e autorização
│   ├── llm_adapter.py                # Adaptador para LLMs (Gemini/DeepSeek)
│   ├── llm_base.py                   # Classes base para LLM
│   ├── llm_service.py                # Serviço de LLM
│   ├── permissions.py                # Sistema de permissões
│   │
│   ├── agents/                       # Agentes específicos
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── bi_agent_nodes.py        # Nós do agent BI
│   │   ├── caculinha_bi_agent.py
│   │   ├── caculinha_dev_agent.py
│   │   ├── code_gen_agent.py        # Gerador de código
│   │   ├── conversational_reasoning_node.py
│   │   ├── data_sync_agent.py
│   │   ├── polars_load_data.py
│   │   ├── product_agent.py
│   │   ├── prompt_loader.py
│   │   ├── tool_agent.py
│   │   └── tests/
│   │       └── test_code_gen_integration.py
│   │
│   ├── business_intelligence/        # Módulo BI
│   │   ├── agent_graph_cache.py
│   │   ├── generic_query_executor.py
│   │   ├── intent_classifier.py
│   │   ├── query_cache.py
│   │   └── __init__.py
│   │
│   ├── connectivity/                 # Camada de Conectividade
│   │   ├── base.py
│   │   ├── hybrid_adapter.py         # Adaptador híbrido
│   │   ├── parquet_adapter.py        # Leitura de Parquet
│   │   ├── polars_dask_adapter.py
│   │   ├── safe_parquet_adapter.py
│   │   └── sql_server_adapter.py     # Conexão SQL Server
│   │
│   ├── database/                     # Modelos e Conexão DB
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── sql_server_auth_db.py
│   │   └── __init__.py
│   │
│   ├── factory/                      # Factory Pattern
│   │   └── component_factory.py      # Factory para LLM adaptadores
│   │
│   ├── graph/                        # LangGraph Orquestração
│   │   ├── agent.py
│   │   ├── graph_builder.py
│   │   └── __init__.py
│   │
│   ├── learning/                     # Sistema de Aprendizado
│   │   ├── dynamic_prompt.py
│   │   ├── error_analyzer.py
│   │   ├── feedback_collector.py
│   │   ├── feedback_system.py
│   │   ├── few_shot_manager.py
│   │   ├── pattern_matcher.py
│   │   ├── self_healing_system.py
│   │   └── __init__.py
│   │
│   ├── mcp/                          # Model Context Protocol
│   │   ├── mcp_manager.py
│   │   ├── mock_data.py
│   │   ├── query_adapter.py
│   │   ├── sqlserver_adapter.py
│   │   ├── sqlserver_mcp_adapter.py
│   │   ├── __init__.py
│   │   └── interfaces/
│   │       └── mcp_adapter_interface.py
│   │
│   ├── monitoring/                   # Métricas e Monitoramento
│   │   └── metrics_dashboard.py
│   │
│   ├── prompts/                      # Templates de Prompts
│   │   └── (arquivos de template)
│   │
│   ├── rag/                          # Retrieval Augmented Generation
│   │   ├── example_collector.py
│   │   ├── query_retriever.py
│   │   └── __init__.py
│   │
│   ├── security/                     # Segurança e Validação
│   │   ├── data_masking.py
│   │   ├── input_validator.py
│   │   ├── rate_limiter.py
│   │   └── __init__.py
│   │
│   ├── tools/                        # Ferramentas de Utilidade
│   │   ├── check_gui_dependencies.py
│   │   ├── check_integration.py
│   │   ├── data_tools.py
│   │   ├── debug_server.py
│   │   ├── graph_integration.py
│   │   ├── mcp_sql_server_tools.py
│   │   ├── query_history.py
│   │   ├── sql_server_tools.py
│   │   ├── une_tools.py
│   │   ├── verify_imports.py
│   │   └── __init__.py
│   │
│   ├── ui/                           # Componentes de UI
│   │   ├── conversational_ui_components.py
│   │   └── __init__.py
│   │
│   ├── utils/                        # Utilitários Gerais
│   │   ├── cache_cleaner.py
│   │   ├── chart_generator.py
│   │   ├── column_validator.py
│   │   ├── context.py
│   │   ├── correlation.py
│   │   ├── correlation_id.py
│   │   ├── dataframe_formatter.py
│   │   ├── db_check.py
│   │   ├── db_config.py
│   │   ├── db_connection.py
│   │   ├── db_fallback.py
│   │   ├── db_structure_loader.py
│   │   ├── db_utils.py
│   │   ├── directory_setup.py
│   │   ├── env_setup.py
│   │   ├── error_handler.py
│   │   ├── event_manager.py
│   │   ├── field_mapper.py
│   │   ├── hot_reload.py
│   │   ├── json_utils.py
│   │   ├── langchain_utils.py
│   │   ├── logger_config.py
│   │   ├── memory_optimizer.py
│   │   ├── openai_config.py
│   │   ├── path_validator.py
│   │   ├── performance_integration.py
│   │   ├── performance_tracker.py
│   │   ├── query_history.py
│   │   ├── query_optimizer.py
│   │   ├── query_validator.py
│   │   ├── response_cache.py          # Cache de respostas (TTL 6h)
│   │   ├── safe_data_loader.py
│   │   ├── security.py
│   │   ├── security_utils.py
│   │   ├── session_manager.py
│   │   ├── sql_utils.py
│   │   ├── streamlit_stability.py
│   │   ├── text_utils.py
│   │   ├── validators.py
│   │   └── __init__.py
│   │
│   ├── validation/                   # Validação de Código
│   │   ├── code_validator.py
│   │   └── __init__.py
│   │
│   ├── validators/                   # Validadores Adicionais
│   │   ├── schema_validator.py
│   │   └── __init__.py
│   │
│   └── visualization/                # Visualizações
│       ├── advanced_charts.py
│       └── __init__.py
│
├── 📂 pages/                         # ⭐ Páginas Streamlit Multi-Page
│   ├── 01_📊_Metricas.py            # Dashboard de métricas
│   ├── 03_📊_Graficos_Salvos.py     # Galeria de gráficos
│   ├── 04_📈_Monitoramento.py       # Monitoramento em tempo real
│   ├── 05_📚_Exemplos_Perguntas.py  # Exemplos de consultas
│   ├── 06_⚙️_Painel_de_Administração.py  # Admin panel
│   ├── 07_❓_Ajuda.py                # Página de ajuda
│   ├── 08_📦_Transferências.py      # Gestão de transferências
│   ├── 09_📊_Relatório_de_Transferências.py
│   ├── 10_🤖_Gemini_Playground.py   # Teste de LLM
│   ├── 11_🩺_Diagnostico_DB.py      # Diagnóstico de banco
│   ├── 12_🔐_Alterar_Senha.py       # Gerenciamento de senhas
│   ├── 13_📊_Sistema_Aprendizado.py # Sistema de aprendizado
│   ├── 14_⚠️_Rupturas_Críticas.py    # Alertas críticos
│   └── 1_💻_Code_Chat.py             # ✨ NEW: Chat de análise de código
│
├── 📂 config/                        # Configurações
│   ├── database/
│   │   ├── alembic.ini               # Config Alembic
│   │   └── migrations/               # Migrações do banco
│   │       ├── env.py
│   │       └── versions/
│   │           └── d4f68a172d44_create_user_table.py
│   ├── runtime.txt
│   ├── streamlit_secrets.toml        # Secrets do Streamlit
│   ├── column_mapping.py
│   ├── logging_config.py
│   ├── safe_settings.py
│   ├── settings.py
│   ├── streamlit_settings.py
│   ├── une_mapping.py
│   ├── __init__.py
│   └── interfaces/
│       └── config_interface.py
│
├── 📂 data/                          # Dados e Exemplos
│   ├── parquet/
│   │   └── admmat.parquet           # 1.113.822 linhas, 38 UNEs, 761k produtos
│   ├── cache/                        # Cache de respostas
│   ├── input/                        # Dados de entrada
│   ├── learning/                     # Dados de aprendizado
│   ├── query_history/                # Histórico de queries
│   ├── transferencias/               # Dados de transferências
│   ├── catalog_focused.json          # Catálogo de dados
│   ├── query_examples.json           # Exemplos de queries
│   └── query_patterns.json           # Padrões de queries
│
├── 📂 docs/                          # Documentação Técnica
│   ├── README.md                     # Guia principal
│   ├── CONFIGURACAO_API_KEY.md
│   ├── FEEDBACK_INICIAL_IMPLEMENTADO.md
│   ├── GUIA_RAPIDO_API_KEY.md
│   ├── IMPLEMENTATION_CHECKLIST.md
│   ├── INTEGRATION_GUIDE.md
│   ├── IMPACT_SUMMARY.md
│   ├── OTIMIZACOES_PERFORMANCE_FINAL.md
│   ├── PIC_MAPPING.md
│   ├── PROBLEMA_REAL_IDENTIFICADO.md
│   ├── PROBLEMA_STREAMING_DIAGNOSTICO.md
│   ├── prompt_pic_agent_bi_implementation.md
│   ├── RELATORIO_TESTES.md
│   ├── SOLUCAO_FINAL.md
│   ├── SOLUCAO_IMPLEMENTADA.md
│   ├── STREAMING_INTERFACE_LIMPA.md
│   └── (outros docs)
│
├── 📂 reports/                       # Relatórios Gerados
│   └── charts/                       # Gráficos salvos
│
├── 📂 storage/                       # Índices e Cache
│   ├── code_index.json               # Índice do codebase
│   │                                 # - 8.031 arquivos Python
│   │                                 # - 115.213 funções
│   │                                 # - 18.398 classes
│   │                                 # - 2.715.480 linhas
│   └── cache_agent_graph/            # Cache de execução
│
├── 📂 tests/                         # Testes Unitários
│   └── test_code_chat.py             # Testes da página Code Chat
│
├── 📂 tools/                         # Ferramentas Auxiliares
│   ├── autostart_streamlit.py
│   ├── check_dotenv.py
│   ├── verify_imports.py
│   └── write_env.py
│
├── 📂 ui/                            # Componentes de UI Reutilizáveis
│   ├── __init__.py
│   ├── feedback_component.py
│   └── ui_components.py
│
├── 📂 venv/                          # Virtual Environment Python
│   └── (ambiente isolado do projeto)
│
├── 📂 .github/                       # Configurações GitHub
│   └── (CI/CD, workflows, etc)
│
├── 📂 .streamlit/                    # Configuração Streamlit
│   └── config.toml
│
├── 🐍 streamlit_app.py               # ⭐ PONTO DE ENTRADA PRINCIPAL
│   │                                 # - Config básica do Streamlit
│   │                                 # - Carregamento de páginas
│   │                                 # - Integração com core/
│   │
├── 🐍 index_code.py                  # Script de Indexação (117 linhas)
│   │                                 # - Descobre arquivos Python
│   │                                 # - Extrai funções e classes
│   │                                 # - Gera storage/code_index.json
│   │                                 # - Zero dependências pesadas
│   │
├── 📄 README.md                      # Documentação Principal
├── 📄 ESTRUTURA_PROJETO.md           # ✨ NEW: Documentação desta estrutura
├── 📄 requirements.txt                # Dependências (maintém projeto)
├── 📄 requirements.in                 # Source das dependências
├── 📄 pytest.ini                      # Configuração de testes
├── 📄 RUN.bat                         # Script de inicialização rápida
├── 📄 .env                            # Variáveis de ambiente
└── 📄 .gitignore                      # Configuração Git

```

---

## 📊 Estatísticas

| Métrica | Valor |
|---------|-------|
| Total de arquivos na raiz | 18 |
| Total de pastas | 15 |
| Arquivos Python principais | 2 |
| Páginas Streamlit | 14 |
| Módulos em core/ | 40+ |
| Arquivos indexados | 8.031 |
| Funções encontradas | 115.213 |
| Classes encontradas | 18.398 |
| Linhas de código total | 2.715.480 |

---

## 🎯 Propósito de Cada Seção

### `/core` - Coração da Aplicação
Contém toda a lógica de negócio, adaptadores, agentes e sistemas de processamento.

### `/pages` - Interface do Usuário
Páginas Streamlit que compõem a interface do usuário multi-page.

### `/config` - Configurações
Arquivos de configuração, variáveis de ambiente, migrations do banco.

### `/data` - Dados
Dados brutos, cache, exemplos de queries, histórico.

### `/docs` - Documentação
Guias técnicos, implementações, soluções, relatórios.

### `/storage` - Índices
Índice JSON do codebase para buscas rápidas, cache de agentes.

### `/tests` - Testes
Testes unitários e de integração.

### `/venv` - Ambiente Virtual
Dependências Python isoladas do sistema.

---

## 🚀 Como Usar

### Iniciar
```bash
streamlit run streamlit_app.py
# ou
RUN.bat
```

### Indexar Codebase
```bash
python index_code.py
```

### Rodar Testes
```bash
pytest
```

---

**Última atualização**: 05/12/2025  
**Estrutura**: Otimizada e finalizada
