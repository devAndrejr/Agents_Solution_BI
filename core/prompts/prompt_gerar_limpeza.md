# PROMPT: GERAÇÃO DE SCRIPT DE LIMPEZA DE PROJETO

### 1. PERSONA E PAPEL
Você é um Engenheiro de DevOps Sênior, especialista em automação de tarefas e organização de estruturas de projetos de software. A sua tarefa é ler um documento de arquitetura (um "Manifesto") e traduzir as suas recomendações de organização de ficheiros num script executável e seguro.

---

### 2. CONTEXTO E OBJETIVO GERAL
**A SITUAÇÃO ATUAL:**
Eu tenho um projeto Python, o `Agent_BI`, que cresceu de forma orgânica e tem muitos scripts de desenvolvimento, manutenção e pipeline de dados misturados com o código principal da aplicação. O `manifesto_arquitetura_alvo.md` (fornecido abaixo) define uma nova estrutura limpa, que exige o isolamento destes scripts de suporte.

**MEU OBJETIVO FINAL:**
Obter um script PowerShell (`.ps1`) que execute a limpeza estrutural do meu projeto, movendo os diretórios de suporte para uma nova pasta `dev_tools/`, conforme recomendado no manifesto.

---

### 3. TAREFA ESPECÍFICA E IMEDIATA
**SUA TAREFA AGORA:**
Com base no `manifesto_arquitetura_alvo.md` fornecido abaixo, gere o conteúdo de um único script PowerShell chamado `cleanup_project.ps1`.

**Requisitos do Script:**
1.  **Segurança:** O script deve verificar se as pastas existem antes de tentar movê-las para evitar erros.
2.  **Criação do Diretório:** A primeira ação do script deve ser criar a nova pasta `dev_tools` na raiz do projeto.
3.  **Movimentação de Pastas:** O script deve mover os seguintes diretórios da raiz do projeto para dentro de `dev_tools/`, conforme a "Zona 7" do manifesto:
    * `scripts/`
    * `dags/`
    * `tools/` (Apenas se existir uma pasta `tools/` na raiz do projeto).
4.  **Informativo:** O script deve imprimir mensagens na consola a informar o que está a fazer (ex: "A criar o diretório dev_tools...", "A mover a pasta scripts/...").
5.  **Comentários:** O código do script deve ser bem comentado para que eu possa entender cada passo.

---

### 4. DOCUMENTO DE REFERÊNCIA (MANIFESTO)

**Manifesto da Arquitetura Alvo: Agent_BI 3.0**

**Propósito:** Este documento é o mapa definitivo da nova arquitetura do Agent_BI. Ele detalha todos os ficheiros essenciais para o funcionamento do sistema, o seu propósito e as suas interações, servindo como guia para o desenvolvimento, manutenção e futuras expansões.

**Princípios da Arquitetura:**
* Orquestração Centralizada: O LangGraph é o único "cérebro" que gere o fluxo de tarefas.
* Desacoplamento de Camadas: O Frontend (UI) é completamente separado do Backend (Lógica).
* Configuração Unificada: Existe um ponto único de verdade para todas as configurações e segredos.

**Diagrama de Fluxo Simplificado:**
[Apresentação] -> [Gateway de API] -> [Orquestração] -> [Lógica & Ferramentas] -> [Conectividade de Dados]

**Zona 7: Ferramentas de Desenvolvimento e Manutenção (A Oficina)**
*Ficheiros e scripts que são cruciais para o desenvolvimento, mas não para a execução da aplicação em produção. Eles devem ser movidos para uma pasta dev_tools/.*

| Ficheiro Essencial | Propósito na Nova Arquitetura |
| :--- | :--- |
| `scripts/` (diretório) | Contém todos os scripts de pipeline de dados (ETL), limpeza, geração de catálogos, avaliação de agentes, etc. |
| `tools/` (diretório) | Contém scripts de diagnóstico e inspeção de dados. |
| `dags/` (diretório) | Contém a definição do pipeline de dados, que é uma tarefa de manutenção/desenvolvimento. |

---

### 5. FORMATO DE SAÍDA DESEJADO
Gere um único bloco de código PowerShell contendo o script `cleanup_project.ps1` completo. Não inclua nenhum outro texto ou explicação fora do bloco de código.