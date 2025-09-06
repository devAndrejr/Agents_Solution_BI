# Relatório de Arquitetura Alvo: `arquitetura_alvo.md`

## Resumo da Arquitetura Alvo

A arquitetura alvo para o projeto **agente-bi-caculinha** visa criar um sistema de BI conversacional robusto, modular e escalável. A estrutura se baseia em componentes especializados e desacoplados, seguindo as melhores práticas de engenharia de software.

Os pilares da arquitetura são:

1.  **Frontend (UI):** Uma interface de usuário limpa e interativa construída com **Streamlit**. Todos os componentes de UI, estilos e a aplicação principal do Streamlit ficarão centralizados na pasta `ui/` e no arquivo `streamlit_app.py`.

2.  **Orquestração de Agentes (Backend):** O cérebro do sistema, utilizando **LangGraph** para orquestrar um fluxo de múltiplos agentes (MCP - Multi-Agent Collaboration Protocol). Um **Agente Supervisor** (`supervisor.py`) atuará como o ponto de entrada, recebendo as solicitações do usuário e delegando tarefas para agentes especializados.

3.  **Lógica Core e Ferramentas:** A pasta `core/` conterá toda a lógica de negócio. Subpastas como `core/agents`, `core/prompts` e `core/graph` definirão os componentes do sistema de agentes. Crucialmente, as ferramentas dos agentes (`core/agent_tools`) serão refatoradas para interagir diretamente com o **SQL Server**, garantindo que as análises sejam feitas em tempo real sobre a fonte de dados primária, em vez de arquivos Parquet estáticos.

4.  **Pipeline de Dados (ETL):** A pasta `dags/` conterá os pipelines de dados (ex: Airflow) responsáveis por extrair dados de fontes externas, transformá-los e carregá-los no SQL Server. Isso garante que o banco de dados esteja sempre atualizado.

5.  **Scripts e Automações:** A pasta `scripts/` será reorganizada em subdiretórios (`setup`, `maintenance`, `analysis`) para abrigar scripts utilitários, de manutenção e análises pontuais, mantendo o projeto organizado.

## Mapa de Movimentações

A tabela abaixo mapeia a estrutura atual para a arquitetura alvo proposta.

| Arquivo/Pasta Atual                      | Ação       | Destino na Arquitetura Alvo                               | Justificativa                                                                                              |
| ---------------------------------------- | ---------- | --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `streamlit_app.py`                       | Manter     | `streamlit_app.py` (Raiz)                                 | Ponto de entrada da aplicação Streamlit.                                                                   |
| `run_app.py`                             | Excluir    | -                                                         | Script de inicialização redundante. `streamlit run streamlit_app.py` é o padrão.                           |
| `style.css`                              | Mover      | `ui/style.css`                                            | Centraliza todos os arquivos de interface.                                                                 |
| `pages/`                                 | Mover      | `ui/pages/`                                               | Agrupa as páginas do Streamlit junto com o resto da UI.                                                    |
| `core/`                                  | Manter     | `core/`                                                   | Continua sendo o centro da lógica de negócio.                                                              |
| `core/tools/`                            | Renomear   | `core/agent_tools/`                                       | Nome mais descritivo para as ferramentas que o agente LangGraph usará.                                     |
| `tools/`                                 | Mover      | `scripts/analysis/`                                       | Consolida scripts de análise avulsos dentro da pasta de scripts.                                           |
| `scripts/`                               | Reorganizar| `scripts/` (com subpastas `setup`, `maintenance`, etc.)   | Organiza a grande quantidade de scripts por finalidade.                                                    |
| `dags/`                                  | Manter     | `dags/`                                                   | Local correto para os pipelines de dados.                                                                  |
| `data/`                                  | Manter     | `data/`                                                   | Armazena dados, catálogos e schemas.                                                                       |
| `migrations/`                            | Manter     | `migrations/`                                             | Essencial para o versionamento do banco de dados.                                                          |
| `tests/`                                 | Manter     | `tests/`                                                  | Local padrão para todos os testes.                                                                         |
| `limpeza_arquitetura.md`                 | Mover      | `docs/limpeza_arquitetura.md`                             | Relatórios e documentação devem ficar na pasta `docs`.                                                     |
| `relatorio_2808.md`                      | Mover      | `docs/archive/relatorio_2808.md`                          | Arquiva relatórios antigos para referência histórica.                                                      |

## Arquivos a Excluir

- **`read_parquet_temp.py`**, **`scripts/final_cleanup_temp.py`**, **`core/tools/sql_server_tools.py`**: Arquivos vazios ou temporários.
- **`tests/temp_get_product_price.py`**: Teste local e pontual, não faz parte da suíte de testes automatizada.
- **`prompt.md`**, **`prompt_limpeza.md`**: Arquivos de instrução para a IA, não são parte do código do projeto.
- **`scripts/fix_*.py`**, **`scripts/generate_*.py`**, etc.: Muitos scripts na pasta `scripts` são de uso único. Após a reorganização, uma revisão deve ser feita para arquivar ou remover os que não são mais necessários.

## Gaps (o que está faltando)

1.  **Integração Real com SQL Server:** Este é o **principal gap**. A arquitetura alvo pressupõe que os agentes consultem o SQL Server diretamente. Atualmente, as ferramentas em `core/tools/mcp_sql_server_tools.py` leem arquivos Parquet. É necessário **criar um novo conjunto de ferramentas de agente** que se conectem ao SQL Server para executar queries (leitura de dados, busca de produtos, etc.).

2.  **Agente Supervisor (`supervisor.py`):** Não há um arquivo claro que defina o agente orquestrador principal na raiz do projeto. A lógica de orquestração do LangGraph deve ser centralizada em um `supervisor.py` ou em um módulo claro dentro de `core/`, que servirá como o ponto de entrada para o backend.

3.  **Estrutura da Pasta `ui`:** A pasta `ui` existe, mas precisa ser formalmente adotada como o local para todos os componentes do Streamlit, incluindo `pages` e `style.css`.

4.  **Modularização dos Prompts:** Os prompts para os agentes devem ser externalizados e organizados na pasta `core/prompts`, facilitando a edição e o versionamento.

## Sugestões Finais

- **Prioridade 1: Focar na integração com o SQL Server.** A maior parte do valor da arquitetura alvo vem da capacidade de analisar dados em tempo real. A refatoração das ferramentas do agente para usar o SQL Server deve ser a primeira prioridade.
- **Prioridade 2: Implementar o Supervisor e o LangGraph.** Definir o fluxo de orquestração no `supervisor.py` e estruturar o grafo de agentes em `core/graph` tornará o sistema mais robusto e fácil de depurar.
- **Prioridade 3: Executar a Reorganização.** Após as mudanças críticas de código, a reorganização das pastas e a exclusão de arquivos obsoletos podem ser feitas para limpar a base de código, conforme o mapa de movimentações.
