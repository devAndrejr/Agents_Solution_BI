# 🤖 Agent Solution BI - Streamlit Edition

## Sistema de Business Intelligence com IA - Interface Única e Poderosa

**Análise de Dados em Linguagem Natural, 100% Python.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.48+-red.svg)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.6+-orange.svg)](https://langchain.com/langgraph)
[![Polars](https://img.shields.io/badge/Polars-1.34+-yellowgreen.svg)](https://www.pola.rs/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 O Que É?

Agent Solution BI é uma plataforma completa de **Business Intelligence com Inteligência Artificial** construída inteiramente em Python. Ela permite que você analise dados complexos através de **conversação em linguagem natural**.

**Pergunte em português, receba análises, gráficos e insights automáticos!**

```
Você: "Top 10 produtos mais vendidos"
IA:   📊 Gráfico de barras + tabela + insights automáticos
```

## ✨ Funcionalidades Principais

O projeto é uma aplicação Streamlit multipágina (14 páginas), oferecendo um conjunto robusto de ferramentas de BI:

- 🗣️ **Chat com IA** - Faça perguntas complexas em português e receba respostas baseadas em dados.
- 📊 **Gráficos Automáticos** - A IA gera visualizações interativas (Plotly) a partir das suas perguntas.
- 📈 **Dashboards Interativos** - Páginas dedicadas a métricas, monitoramento e relatórios específicos.
- 💾 **Cache Inteligente** - Respostas instantâneas para consultas repetidas (TTL 6 horas).
- 📝 **Histórico Completo** - Todas as suas análises e queries salvas.
- 🔐 **Sistema de Autenticação** - Login de usuário e controle de acesso (implementado via Streamlit).
- 💻 **Code Chat** - ✨ **NOVO** Chat de análise do codebase com RAG baseado em índice JSON (8.031 arquivos indexados).
- 🔍 **Busca Semântica** - Procure por funções, classes e arquivos em todo o codebase.

## 🚀 Quick Start (5 minutos)

### Pré-requisitos

- **Python 3.11+** (testado com Python 3.13.2)
- Uma chave de API do Google Gemini (ou DeepSeek, se configurado)
- Git

### Instalação

#### 1️⃣ Clone o repositório
```bash
git clone https://github.com/devAndrejr/Agents_Solution_BI.git
cd Agents_Solution_BI
```

#### 2️⃣ Crie e ative o ambiente virtual

**No Windows (PowerShell/CMD):**
```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate

# Desativar quando terminar
deactivate
```

**No Linux/macOS (Bash/Zsh):**
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Desativar quando terminar
deactivate
```

#### 3️⃣ Instale as dependências
```bash
pip install -r requirements.txt
```

#### 4️⃣ Configure sua chave de API

**Windows:**
```powershell
# Criar arquivo .env
"GEMINI_API_KEY=sua_chave_gemini_aqui" | Out-File -Encoding UTF8 .env
```

**Linux/macOS:**
```bash
echo "GEMINI_API_KEY=sua_chave_gemini_aqui" > .env
```

#### 5️⃣ Execute a aplicação Streamlit
```bash
streamlit run streamlit_app.py
```

**Pronto!** 🎉 Acesse em `http://localhost:8501`

### Verificar Instalação

Para verificar se tudo foi instalado corretamente:
```bash
python -c "import streamlit; import polars; import plotly; import langchain; print('✅ Todos os módulos OK')"
```

## 🏗️ Arquitetura e Tecnologias Core

O projeto é uma aplicação monolítica em Python com Streamlit como frontend e LangGraph para orquestração de agentes de IA.

| Componente | Tecnologia | Versão | Função |
| :--- | :--- | :--- | :--- |
| **Interface (Frontend)** | Streamlit | 1.52.0 | Dashboards interativos e interface de chat |
| **Orquestração de IA** | LangGraph | Latest | Fluxo de workflow do Agente BI (planejamento → código → execução) |
| **Modelo de Linguagem** | Google Gemini API | 2.5-pro/flash | Interpretação de perguntas e geração de código |
| **Processamento de Dados** | Polars | 1.35.2 | Manipulação rápida de arquivos Parquet (lazy evaluation) |
| **Fallback de Dados** | Dask | Latest | Suporte para arquivos > 500MB |
| **Visualização** | Plotly | 6.3.0 | Gráficos interativos em tempo real |
| **Cache de Respostas** | Customizado | 6h TTL | Economia de créditos API |
| **Dados** | Parquet | 91.8MB | Arquivo único com 97 colunas, 39 UNEs |
| **Python** | CPython | 3.13.2 | Runtime da aplicação

## 🌟 Melhorias Recentes (v1.0.2)

### ✅ Novas Funcionalidades (2025-12-05)

| Funcionalidade | Descrição | Status |
|---|---|---|
| **💻 Code Chat** | Nova página para análise de código com RAG | ✅ Implementado |
| **📊 code_index.json** | Índice de 8.031 arquivos (115k funções, 18k classes) | ✅ Indexado |
| **🎯 Reorganização Completa** | Projeto limpo e otimizado (-55% desordem) | ✅ Concluído |
| **📚 Documentação Visual** | ESTRUTURA_PROJETO.md + ARVORE_VISUAL.md | ✅ Criado |

### ✅ Erros Críticos Resolvidos (Versão 1.0.1 - 2025-12-05)

| Erro | Solução | Status |
|------|---------|--------|
| `.env` UTF-16 BOM encoding | Convertido para UTF-8 puro | ✅ Resolvido |
| `ModuleNotFoundError: openai` | Instalado openai==1.109.1 | ✅ Resolvido |
| `ModuleNotFoundError: langchain_core` | Instalados 4 pacotes LangChain | ✅ Resolvido |
| `ModuleNotFoundError: dask/plotly/pyodbc` | Instalados 6 pacotes adicionais | ✅ Resolvido |
| `UnserializableSessionStateError` (Streamlit) | @st.cache_resource decorator | ✅ Resolvido |
| Agente retornando erro sobre `mes_01-mes_12` | Prompt enriquecido com schema real | ✅ Resolvido |
| `ValueError: Invalid format specifier` (bi_agent_nodes.py) | Escapar chaves em f-string com `{{ }}` | ✅ Resolvido |
| `FileNotFoundError: admmat_extended.parquet` (Transferências) | Corrigir paths para `admmat.parquet` (4 locais) | ✅ Resolvido |

### 📊 Reorganização e Otimizações (2025-12-05)

**Projeto completamente reorganizado e otimizado:**
- ✅ Removidos 14 arquivos antigos (testes, resumos obsoletos)
- ✅ Removidas 2 pastas redundantes (ambiente_python/, logs/)
- ✅ Criada pasta /tests com testes centralizados
- ✅ Documentação nova: ESTRUTURA_PROJETO.md + ARVORE_VISUAL.md
- ✅ Raiz reduzida de 40+ para 18 itens (-55% desordem)
- ✅ **Nova página**: pages/1_💻_Code_Chat.py com RAG baseado em índice JSON
- ✅ **Novo script**: index_code.py reescrito (117 linhas, zero deps pesadas)

### 📊 Validação Completa

Todos os componentes testados e validados:
- ✅ Ambiente virtual e dependências
- ✅ Carregamento de arquivo Parquet (1.113.822 linhas)
- ✅ LLM adapter (Gemini) funcional com cache 6h
- ✅ Geração de gráficos Plotly
- ✅ Serialização Streamlit
- ✅ Agente respondendo corretamente
- ✅ Code Chat funcionando com índice JSON (8.031 arquivos)
- ✅ Todos os testes passando (4/4 validações)

## 📚 Documentação Detalhada

### Estrutura e Referência
| Documento | Descrição |
|-----------|----------|
| **[ESTRUTURA_PROJETO.md](ESTRUTURA_PROJETO.md)** | ✨ **NOVO** Referência completa da estrutura |
| **[ARVORE_VISUAL.md](ARVORE_VISUAL.md)** | ✨ **NOVO** Árvore visual com todos os arquivos |

### Histórico de Correções e Otimizações
| Documento | Descrição |
|-----------|----------|
| [docs/RESOLUCAO_ERROS_CONSULTA_AGENTE.md](docs/RESOLUCAO_ERROS_CONSULTA_AGENTE.md) | Resolução detalhada dos 8 erros críticos (2025-12-05) |
| [docs/OTIMIZACOES_PERFORMANCE_FINAL.md](docs/OTIMIZACOES_PERFORMANCE_FINAL.md) | Análise de performance e otimizações |
| [docs/INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md) | Guia de integração de componentes |
| [docs/IMPLEMENTATION_CHECKLIST.md](docs/IMPLEMENTATION_CHECKLIST.md) | Checklist de implementação |

## 📚 Estrutura do Projeto

```
Agents_Solution_BI/
├── 📂 core/                    # Lógica principal (40+ módulos)
│   ├── agents/                 # Agentes específicos (BI, código, dados)
│   ├── business_intelligence/  # Módulo BI (classifier, cache, executor)
│   ├── connectivity/           # Adaptadores (Parquet, SQL Server, Híbrido)
│   ├── database/               # Modelos e conexão DB
│   ├── factory/                # ComponentFactory para LLM
│   ├── graph/                  # LangGraph orquestração
│   ├── learning/               # Sistema de aprendizado
│   ├── security/               # Validação e rate limiting
│   ├── utils/                  # Utilitários (cache, logging, etc)
│   └── ... (10 outros módulos)
├── 📂 pages/                   # Páginas Streamlit (14 páginas)
│   ├── 01_📊_Metricas.py
│   ├── 08_📦_Transferências.py
│   ├── 1_💻_Code_Chat.py       # ✨ NEW: Chat de análise de código
│   └── ... (11 outras páginas)
├── 📂 config/                  # Configurações, migrations Alembic
├── 📂 data/                    # Parquets, cache, exemplos, histórico
├── 📂 docs/                    # Documentação técnica
├── 📂 reports/                 # Relatórios e gráficos gerados
├── 📂 storage/                 # Índices (code_index.json)
├── 📂 tests/                   # Testes unitários
├── 📂 tools/                   # Ferramentas auxiliares
├── 📂 ui/                      # Componentes de UI
├── 📂 venv/                    # Virtual environment
├── 🐍 streamlit_app.py         # Ponto de entrada principal
├── 🐍 index_code.py            # Script de indexação (117 linhas, zero deps pesadas)
├── 📄 README.md                # Este arquivo
├── 📄 ESTRUTURA_PROJETO.md     # ✨ Documentação completa da estrutura
├── 📄 ARVORE_VISUAL.md         # ✨ Árvore visual do projeto
├── 📄 requirements.txt         # Dependências do projeto
├── 📄 pytest.ini               # Configuração de testes
└── 📄 RUN.bat                  # Script de inicialização rápida
```

**Para mais detalhes**, consulte:
- **[ESTRUTURA_PROJETO.md](ESTRUTURA_PROJETO.md)** - Referência completa
- **[ARVORE_VISUAL.md](ARVORE_VISUAL.md)** - Visualização visual com descrições

## 🔧 Configuração

### Variáveis de Ambiente (`.env`)

```env
# Obrigatório
GEMINI_API_KEY=sua_chave_gemini

# Opcional (para integração com SQL Server)
SQL_SERVER=localhost
SQL_DATABASE=db_name
SQL_USERNAME=user
SQL_PASSWORD=pass

# Opcional (para usar DeepSeek como LLM)
DEEPSEEK_API_KEY=sua_chave_deepseek
```

## 🎯 Casos de Uso

- 📊 **Análise de Vendas** - Rankings, top produtos, comparações.
- 📦 **Gestão de Estoque** - Rupturas, giro, previsões.
- 🏪 **Performance de Lojas** - Comparações entre unidades.
- 🎯 **Inteligência de Mercado** - Tendências, segmentação.
- 📈 **KPIs Executivos** - Dashboards gerenciais.

## 🤝 Contribuindo

1. Fork o projeto
2. Criar branch (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'feat: Adiciona AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

---

**Made with ❤️ by Agent Solution BI Team**

**Version**: 1.0.2 | **Última atualização**: 2025-12-05 | **Status**: ✅ **Code Chat + Reorganização Completa - Pronto para produção**

---

### 📞 Suporte e Dúvidas

- 📖 Leia primeiro: [REVISAO_ERROS_MITIGADOS.md](REVISAO_ERROS_MITIGADOS.md)
- 🚀 Primeiros passos: Siga as instruções acima em "Quick Start"
- 💬 Perguntas? Consulte a seção [🔧 Configuração](#-configuração)
