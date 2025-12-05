# Estrutura do Projeto - Agents_Solution_BI

## 📋 Visão Geral da Raiz

```
Agents_Solution_BI/
├── 📂 core/              # Lógica principal da aplicação
├── 📂 pages/             # Páginas multi-page do Streamlit
├── 📂 config/            # Arquivos de configuração
├── 📂 data/              # Dados (cache, parquet, exemplos)
├── 📂 docs/              # Documentação técnica
├── 📂 reports/           # Relatórios gerados
├── 📂 storage/           # Índices e caches de código
├── 📂 tests/             # Testes unitários
├── 📂 tools/             # Ferramentas auxiliares
├── 📂 ui/                # Componentes de UI reutilizáveis
├── 📂 venv/              # Ambiente virtual Python
├── 📂 .github/           # Configurações GitHub (CI/CD)
├── 📂 .streamlit/        # Configuração do Streamlit
├── 📜 streamlit_app.py   # Arquivo principal (ponto de entrada)
├── 📜 index_code.py      # Script para indexar codebase
├── 📜 README.md          # Documentação principal
├── 📜 requirements.txt   # Dependências do projeto
├── 📜 requirements.in    # Source das dependências
├── 📜 pytest.ini         # Configuração de testes
├── 📜 RUN.bat            # Script de inicialização (Windows)
├── 📄 .env               # Variáveis de ambiente
└── 📄 .gitignore         # Configuração do Git
```

---

## 🗂️ Estrutura Detalhada

### `/core` - Lógica Principal
```
core/
├── agent_state.py              # Estado do agente (TypedDict)
├── auth.py                      # Autenticação e autorização
├── llm_adapter.py              # Adaptador para LLMs (Gemini/DeepSeek)
├── llm_base.py                 # Classes base para LLM
├── llm_service.py              # Serviço de LLM
├── permissions.py              # Sistema de permissões
├── __init__.py
├── agents/                      # Agentes específicos
│   ├── bi_agent_nodes.py
│   ├── code_gen_agent.py
│   ├── data_sync_agent.py
│   └── ...
├── business_intelligence/       # Módulo BI
├── connectivity/                # Conexão com dados
│   ├── parquet_adapter.py
│   ├── sql_server_adapter.py
│   └── ...
├── database/                    # Modelos e conexão DB
├── factory/                     # Factory pattern (ComponentFactory)
├── graph/                       # LangGraph orquestração
├── learning/                    # Sistema de aprendizado
├── mcp/                         # Model Context Protocol
├── monitoring/                  # Métricas e monitoramento
├── prompts/                     # Templates de prompts
├── rag/                         # Retrieval Augmented Generation
├── security/                    # Segurança e validação
├── tools/                       # Ferramentas de utilidade
├── ui/                          # Componentes de UI
├── utils/                       # Utilitários gerais
├── validation/                  # Validação de código
└── visualization/               # Visualizações
```

### `/pages` - Páginas Streamlit Multi-Page
```
pages/
├── 01_📊_Metricas.py           # Dashboard de métricas
├── 03_📊_Graficos_Salvos.py    # Galeria de gráficos
├── 04_📈_Monitoramento.py      # Monitoramento em tempo real
├── 05_📚_Exemplos_Perguntas.py # Exemplos de consultas
├── 06_⚙️_Painel_de_Administração.py  # Admin panel
├── 07_❓_Ajuda.py               # Página de ajuda
├── 08_📦_Transferências.py     # Gestão de transferências
├── 09_📊_Relatório_de_Transferências.py
├── 10_🤖_Gemini_Playground.py  # Teste de LLM
├── 11_🩺_Diagnostico_DB.py     # Diagnóstico de banco
├── 12_🔐_Alterar_Senha.py      # Gerenciamento de senhas
├── 13_📊_Sistema_Aprendizado.py # Sistema de aprendizado
├── 14_⚠️_Rupturas_Críticas.py   # Alertas críticos
└── 1_💻_Code_Chat.py            # ✨ NEW: Chat de análise de código
```

### `/config` - Configurações
```
config/
├── runtime.txt           # Versão de runtime
├── streamlit_secrets.toml # Secrets do Streamlit
├── database/             # Migrações Alembic
│   ├── alembic.ini
│   └── migrations/
└── ...
```

### `/data` - Dados
```
data/
├── parquet/              # Arquivos Parquet
│   └── admmat.parquet    # 1.1M linhas de dados
├── cache/                # Cache de respostas
├── input/                # Dados de entrada
├── learning/             # Dados de aprendizado
├── query_history/        # Histórico de queries
├── transferencias/       # Dados de transferências
└── *.json                # Padrões e exemplos de query
```

### `/storage` - Índices e Cache
```
storage/
├── code_index.json       # Índice do codebase (8.031 arquivos)
└── cache_agent_graph/    # Cache de execução
```

### `/docs` - Documentação
```
docs/
├── README.md             # Guia principal
├── GUIA_RAPIDO_API_KEY.md
├── CONFIGURACAO_API_KEY.md
├── IMPLEMENTATION_CHECKLIST.md
└── ...
```

### `/tests` - Testes
```
tests/
└── test_code_chat.py     # Testes da página Code Chat
```

---

## 🚀 Como Usar

### Iniciar a Aplicação
```bash
# Windows
RUN.bat

# Ou manualmente
streamlit run streamlit_app.py
```

### Indexar o Codebase
```bash
python index_code.py
```

### Executar Testes
```bash
pytest
```

---

## 🔄 Reorganização Realizada (05/12/2025)

### ✅ Arquivos Movidos
- `test_code_chat.py` → `tests/test_code_chat.py`

### ✅ Arquivos Removidos
- `test_agent_response.py`
- `test_env_and_adapters.py`
- `test_feedback_inicial.py`
- `test_integrated_validation.py`
- `test_parquet_data.py`
- `test_prompt_update.py`
- `test_quick_wins.py`
- `test_simple.py`
- `test_syntax_fix.py`
- `cli_query.py`
- `RESOLUCAO_COMPLETA_VISAO_GERAL.txt`
- `RESUMO_FINAL.txt`
- `RESUMO_RESOLUCAO_ERROS_FINAL.md`
- `REVISAO_ERROS_MITIGADOS.md`

### ✅ Pastas Removidas
- `ambiente_python/` (redundante com venv/)
- `logs/` (vazio/desnecessário)

### ✅ Arquivos Mantidos na Raiz
- `streamlit_app.py` - Ponto de entrada principal
- `index_code.py` - Script de indexação
- `README.md` - Documentação
- `requirements.txt` - Dependências
- `requirements.in` - Source das dependências
- `pytest.ini` - Configuração de testes
- `RUN.bat` - Inicialização rápida

---

## 📊 Estatísticas do Projeto

| Métrica | Valor |
|---------|-------|
| **Arquivos Python em core/** | 40+ |
| **Páginas Streamlit** | 14 |
| **Arquivos indexados (code_index.json)** | 8.031 |
| **Funções encontradas** | 115.213 |
| **Classes encontradas** | 18.398 |
| **Linhas de código** | 2.715.480 |

---

## 🎯 Componentes-Chave

### LangGraph Agent
- **Localização**: `core/graph/`
- **Função**: Orquestração de workflow de análise BI

### ComponentFactory
- **Localização**: `core/factory/component_factory.py`
- **Função**: Factory pattern para criar adaptadores LLM com fallback automático

### Adaptadores de Conectividade
- **Parquet**: `core/connectivity/parquet_adapter.py`
- **SQL Server**: `core/connectivity/sql_server_adapter.py`
- **Híbrido**: `core/connectivity/hybrid_adapter.py`

### Novo: Code Chat
- **Localização**: `pages/1_💻_Code_Chat.py`
- **Função**: Chat interativo para análise de código com RAG baseado em índice JSON

---

## ✨ Últimas Mudanças

### Adições Recentes (05/12/2025)
1. ✅ `pages/1_💻_Code_Chat.py` - Página de chat para análise de código
2. ✅ `index_code.py` reescrito - Versão otimizada sem LlamaIndex
3. ✅ `tests/test_code_chat.py` - Testes da nova página
4. ✅ Reorganização completa da raiz do projeto

### Melhorias de Performance
- Remoção de dependências pesadas (llama_index)
- Índice JSON otimizado (8.031 arquivos, 2.7M+ linhas)
- Cache de respostas com TTL de 6 horas
- Lazy loading de módulos pesados

---

**Última atualização**: 05/12/2025  
**Status**: ✅ Projeto organizado e otimizado
