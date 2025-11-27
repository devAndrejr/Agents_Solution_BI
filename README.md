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

O projeto é uma aplicação Streamlit multipágina, oferecendo um conjunto robusto de ferramentas de BI:

- 🗣️ **Chat com IA** - Faça perguntas complexas em português e receba respostas baseadas em dados.
- 📊 **Gráficos Automáticos** - A IA gera visualizações interativas (Plotly) a partir das suas perguntas.
- 📈 **Dashboards Interativos** - Páginas dedicadas a métricas, monitoramento e relatórios específicos.
- 💾 **Cache Inteligente** - Respostas instantâneas para consultas repetidas.
- 📝 **Histórico Completo** - Todas as suas análises e queries salvas.
- 🔐 **Sistema de Autenticação** - Login de usuário e controle de acesso (implementado via Streamlit).

## 🚀 Quick Start (5 minutos)

### Pré-requisitos

- Python 3.11+
- Uma chave de API do Google Gemini (ou DeepSeek, se configurado).

```bash
# 1. Clone o repositório
git clone https://github.com/devAndrejr/Agents_Solution_BI Agents_Solution_BI
cd Agents_Solution_BI

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure sua chave de API (crie o arquivo .env)
echo "GEMINI_API_KEY=sua_chave_gemini" > .env

# 5. Execute a aplicação Streamlit
streamlit run streamlit_app.py
```

**Pronto!** Acesse a aplicação em `http://localhost:8501` (ou a porta indicada pelo Streamlit).

## 🏗️ Arquitetura e Tecnologias Core

O projeto é uma aplicação monolítica em Python, onde a interface (Streamlit) e o "backend" (lógica de IA e dados) rodam no mesmo processo.

| Componente | Tecnologia | Função |
| :--- | :--- | :--- |
| **Interface (Frontend)** | **Streamlit** | Criação rápida de dashboards e interface de chat multipágina. |
| **Orquestração de IA** | **LangGraph** | Gerencia o fluxo de trabalho do Agente de BI (planejamento, geração de código, execução). |
| **Modelo de Linguagem (LLM)** | **Google Gemini** | O cérebro do sistema, responsável por interpretar perguntas e gerar código de análise. |
| **Processamento de Dados** | **Polars / Dask** | Bibliotecas de alta performance para manipulação e análise de grandes volumes de dados (Parquet). |
| **Visualização** | **Plotly / Seaborn** | Geração de gráficos interativos e estáticos a partir dos resultados das análises. |
| **Persistência** | **SQLite** | Usado para checkpoints do LangGraph e histórico de queries. |

## 🌟 Melhorias Recentes

Para um histórico detalhado das correções e otimizações, consulte os documentos abaixo:

| Documento | Descrição |
|-----------|-----------|
| [QUICK_WINS_IMPLEMENTADOS.md](QUICK_WINS_IMPLEMENTADOS.md) | Lista de melhorias rápidas e de alto impacto implementadas. |
| [CORRECOES_APLICADAS.md](CORRECOES_APLICADAS.md) | Detalhamento das correções de bugs e ajustes de estabilidade. |
| [ANALISE_PERFORMANCE_PROFUNDA.md](ANALISE_PERFORMANCE_PROFUNDA.md) | Análise aprofundada e otimizações de performance do sistema. |
| [RESULTADO_FINAL_TESTES.md](RESULTADO_FINAL_TESTES.md) | Sumário dos resultados após a bateria final de testes. |

## 📚 Estrutura do Projeto

```
.
├── core/                   # Lógica de negócio, adaptadores de dados e agentes de IA
│   ├── config/             # Configurações (logging, settings)
│   ├── connectivity/       # Adaptação para SQL Server e Parquet
│   ├── database/           # Lógica de banco de dados (SQLite, SQL Server)
│   ├── llm_service/        # Adaptação para Gemini/DeepSeek
│   ├── tools/              # Ferramentas que o Agente de BI pode usar
│   └── utils/              # Funções utilitárias (cache, segurança)
├── data/                   # Local para arquivos de dados (e.g., Parquet)
├── pages/                  # Páginas adicionais do Streamlit (dashboards, relatórios)
├── reports/                # Local para gráficos e relatórios gerados
├── ui/                     # Componentes de UI customizados do Streamlit
├── requirements.txt        # Dependências do projeto
├── streamlit_app.py        # Arquivo principal da aplicação Streamlit
└── README.md               # Este arquivo
```

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

**Version**: 1.0.0 | **Date**: 2025-11-27 | **Status**: ✅ Production Ready

[📖 Leia a Arquitetura (ARQUITETURA_MULTI_INTERFACE.md)](ARQUITETURA_MULTI_INTERFACE.md) | [🚀 Início Rápido (QUICK_START_ATUALIZADO.md)](QUICK_START_ATUALIZADO.md)
