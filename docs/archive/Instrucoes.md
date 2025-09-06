# INSTRUÇÃO PARA O MODELO GEMINI

**Persona:** Você é um engenheiro de software sênior especializado em arquitetura de sistemas, segurança e MLOps. Sua tarefa é refatorar o projeto "Caçulinha BI" para melhorar sua manutenibilidade, segurança e eficiência.

**Contexto:** Analisei o projeto e identifiquei vários pontos de melhoria, resumidos no arquivo `Relatorio_integracao_1308.md`. O projeto utiliza Python, SQL Server, Parquet e a API da OpenAI, com uma interface em Streamlit.

**Objetivo:** Modifique a estrutura de arquivos e o código existente para implementar as seguintes melhorias. Pense passo a passo, analisando cada tarefa antes de gerar o código ou a estrutura de arquivos final. Para cada etapa, explique brevemente a alteração que você está fazendo.

---

**TAREFAS A SEREM EXECUTADAS:**

**Tarefa 1: Gestão de Configuração e Segurança**

1.1. **Refatorar Gestão de Segredos:**
    - Modifique o arquivo `core/llm_adapter.py` para parar de ler a chave da API da OpenAI diretamente do ambiente.
    - Implemente o uso da biblioteca `python-decouple` para carregar a `OPENAI_API_KEY`.
    - Crie um arquivo `.env.example` na raiz do projeto com o conteúdo: `OPENAI_API_KEY=sua_chave_aqui`.
    - Adicione o arquivo `.env` ao final do arquivo `.gitignore`.

1.3. **Configuração LangSmith (Opcional):**
    - Para habilitar o rastreamento detalhado com LangSmith, adicione as seguintes variáveis ao seu arquivo `.env`:
      `LANGCHAIN_TRACING_V2=true`
      `LANGCHAIN_API_KEY=sua_chave_langsmith_aqui`
      `LANGCHAIN_PROJECT=caculinha-bi-project`
    - Certifique-se de que a biblioteca `langsmith` esteja instalada (já deve estar via `requirements.txt`).

1.2. **Segurança do Banco de Autenticação:**
    - Analise o arquivo `core/auth.py`. Se ele estiver manipulando senhas em texto plano, refatore-o para usar a biblioteca `passlib` para hashear e verificar as senhas com um método seguro (ex: `bcrypt`).
    - Adicione um comentário no topo de `core/auth.py` explicando a importância de usar hashes para senhas.

---

**Tarefa 2: Automação e Otimização do Fluxo de Dados**

2.1. **Estrutura para Orquestração:**
    - Crie uma nova pasta na raiz chamada `dags/` (seguindo o padrão de ferramentas como Airflow/Mage).
    - Dentro de `dags/`, crie um script Python chamado `pipeline_dados_caculinha.py`.
    - Neste script, esboce uma função principal que defina a sequência de execução dos scripts existentes:
      1. `scripts/export_sqlserver_to_parquet.py`
      2. `scripts/clean_parquet_data.py`
      3. `scripts/merge_parquets.py`
    - Adicione comentários no script explicando que ele serve como um blueprint para uma futura implementação com uma ferramenta de orquestração.

---

**Tarefa 3: Organização e Limpeza do Código**

3.1. **Criar `.gitignore` Abrangente:**
    - Crie ou substitua o arquivo `.gitignore` na raiz do projeto. Ele deve incluir regras para ignorar:
      - Arquivos de cache do Python (`__pycache__/`)
      - Caches de ferramentas (`.mypy_cache/`, `.pytest_cache/`)
      - Arquivos de configuração de SO (`desktop.ini`)
      - Arquivos de ambiente (`.env`)
      - Bancos de dados locais (`*.db`, `*.sqlite3`)
      - Pastas de build e distribuição (`build/`, `dist/`)

3.2. **Reorganizar Scripts de Uso Único:**
    - Crie uma nova pasta na raiz chamada `tools/`.
    - Mova os seguintes scripts da pasta `scripts/` para `tools/`:
      - `analisar_logs.py`
      - `diagnose_data_types.py`
      - `inspect_column.py`
      - `inspect_parquet.py`
    - Sugira a exclusão dos seguintes scripts, adicionando um comentário sobre o motivo: `delete_unnecessary_files.bat` e `final_cleanup_temp.py`.

---

**Tarefa 4: Documentação e Manutenibilidade**

4.1. **Centralizar Documentação:**
    - Verifique o conteúdo de `Melhorias_Projeto.txt` e `plano_de_melhorias.md`.
    - Crie um novo arquivo `README.md` na raiz do projeto (ou atualize o existente).
    - O novo `README.md` deve conter:
      - Uma breve descrição do projeto "Caçulinha BI".
      - Instruções claras de setup (como instalar dependências, configurar o `.env`).
      - Uma seção "Arquitetura do Projeto", explicando brevemente a função das pastas principais (`core`, `scripts`, `data`, `pages`, `tools`).
      - Uma nota indicando que a documentação antiga (`docs/archive/`, `docs/historico/`, `Melhorias_Projeto.txt`) está obsoleta e será arquivada.

---

**Tarefa 5: Arquitetura do Agente e LLM**

5.1. **Desacoplar Adaptador do LLM:**
    - Crie um novo arquivo em `core/llm_base.py`. Nele, defina uma classe base abstrata (usando o módulo `abc`) chamada `BaseLLMAdapter` com um método abstrato `get_completion(prompt: str) -> str`.
    - Modifique a classe existente em `core/llm_adapter.py` para que ela herde de `BaseLLMAdapter`.
    - Atualize o arquivo `core/query_processor.py` para que ele dependa da classe base (`BaseLLMAdapter`) em vez da implementação concreta da OpenAI, demonstrando o princípio da inversão de dependência.

Por favor, gere a estrutura de arquivos atualizada e o conteúdo dos arquivos modificados ou criados.