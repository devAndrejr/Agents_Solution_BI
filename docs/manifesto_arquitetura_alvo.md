Manifesto da Arquitetura Alvo: Agent_BI 3.0
Propósito: Este documento é o mapa definitivo da nova arquitetura do Agent_BI. Ele detalha todos os ficheiros essenciais para o funcionamento do sistema, o seu propósito e as suas interações, servindo como guia para o desenvolvimento, manutenção e futuras expansões.

Princípios da Arquitetura
A nova estrutura opera sob três princípios fundamentais:

Orquestração Centralizada: O LangGraph é o único "cérebro" que gere o fluxo de tarefas.

Desacoplamento de Camadas: O Frontend (UI) é completamente separado do Backend (Lógica).

Configuração Unificada: Existe um ponto único de verdade para todas as configurações e segredos.

Diagrama de Fluxo Simplificado
O fluxo de uma consulta do utilizador segue um caminho claro e previsível através das zonas funcionais do sistema:

[Apresentação] -> [Gateway de API] -> [Orquestração] -> [Lógica & Ferramentas] -> [Conectividade de Dados]

Mapeamento das Zonas Funcionais e Ficheiros Essenciais
Zona 1: Apresentação e Interação com o Utilizador (O Rosto)
Responsável por toda a interação com o utilizador. É uma camada "pura" de apresentação, sem lógica de negócio.

Ficheiro Essencial

Propósito na Nova Arquitetura

Principais Interações

streamlit_app.py

Ponto de entrada único para a interface do utilizador. Responsável por renderizar o chat e os resultados.

Comunica exclusivamente com o Gateway de API (main.py) via requisições HTTP.

pages/ (diretório)

Contém as diferentes páginas da aplicação Streamlit (Dashboard, Monitoramento, etc.).

Interage com streamlit_app.py para criar a navegação.

ui/ui_components.py

Fornece funções reutilizáveis para a UI, como a geração de links para download e customizações de gráficos.

É importado e utilizado por streamlit_app.py e pelos ficheiros em pages/.

Zona 2: Gateway de Serviços (A Porta de Entrada)
A única porta de entrada para a lógica do sistema. Protege e expõe o "cérebro" do agente ao mundo exterior.

Ficheiro Essencial

Propósito na Nova Arquitetura

Principais Interações

main.py

Backend único da aplicação, construído com FastAPI. Responsável por receber requisições, autenticar e invocar o orquestrador.

Recebe chamadas do Frontend (streamlit_app.py). Invoca o Orquestrador (GraphBuilder).

core/security.py

Contém a lógica de segurança da API, como a verificação de tokens JWT.

Utilizado pelo main.py para proteger os endpoints.

core/schemas.py

Define os "contratos" de dados (modelos Pydantic) para as requisições e respostas da API.

Usado pelo main.py para validar os dados de entrada e saída.

Zona 3: Orquestração e Inteligência (O Cérebro)
O coração do sistema. Decide "o que fazer" e "quem deve fazer".

Ficheiro Essencial

Propósito na Nova Arquitetura

Principais Interações

core/graph/graph_builder.py

Constrói e compila o StateGraph do LangGraph. Define a máquina de estados, os nós e as arestas condicionais que representam o fluxo de raciocínio do agente. É o orquestrador definitivo.

Importa e orquestra os Nós do Agente (bi_agent_nodes.py). Recebe dependências (como o DatabaseAdapter) para injetar nos nós.

Zona 4: Lógica dos Agentes (Os Especialistas)
Contém a lógica de negócio de cada passo que o agente pode tomar. São os "operários" da linha de montagem.

Ficheiro Essencial

Propósito na Nova Arquitetura

Principais Interações

core/agents/bi_agent_nodes.py

(Ficheiro Novo/Refatorado) Contém as funções Python que são os "nós" do grafo (ex: classify_intent, generate_plotly_spec).

É importado pelo GraphBuilder. Utiliza o llm_adapter, outras ferramentas (data_tools) e agentes especialistas.

core/agents/code_gen_agent.py

Um agente especialista chamado por um nó. A sua única função é gerar código (SQL/Python) para responder a perguntas complexas.

É chamado por um nó definido em bi_agent_nodes.py.

core/agents/base_agent.py

Fornece uma classe base com funcionalidades comuns (logging, etc.) para os agentes.

É herdado pelos agentes especialistas como code_gen_agent.py.

Zona 5: Ferramentas e Conectividade (As Mãos)
Componentes que executam ações no "mundo real", como aceder a bases de dados ou a APIs externas.

Ficheiro Essencial

Propósito na Nova Arquitetura

Principais Interações

core/tools/data_tools.py

Define as ferramentas (@tool) que os nós dos agentes podem executar (ex: fetch_data_from_query).

São chamadas pelos nós em bi_agent_nodes.py.

core/connectivity/sql_server_adapter.py

Implementação concreta do DatabaseAdapter para o SQL Server. Contém toda a lógica de conexão e execução de queries.

É utilizado pelas data_tools. A sua instância é criada no main.py e injetada no GraphBuilder.

core/connectivity/base.py

Define a interface abstrata (DatabaseAdapter), garantindo que qualquer base de dados futura siga o mesmo "contrato".

É a base para o sql_server_adapter.py.

core/llm_adapter.py

Abstrai a comunicação com o provedor de LLM (ex: OpenAI), centralizando a lógica de chamadas de API.

Utilizado pelos nós em bi_agent_nodes.py que precisam de usar a IA.

Zona 6: Configuração e Estado (A Memória)
Ficheiros que gerem o estado e a configuração da aplicação.

Ficheiro Essencial

Propósito na Nova Arquitetura

Principais Interações

core/config/settings.py

Carrega e valida todas as configurações (chaves de API, strings de conexão) a partir do ficheiro .env, usando pydantic-settings.

É importado por todos os módulos que precisam de acesso a configurações, como o main.py.

.env

Ficheiro na raiz do projeto que armazena todas as variáveis de ambiente e segredos. Não deve ser versionado no Git.

É lido pelo settings.py.

core/agent_state.py

Define a estrutura de dados (AgentState) que flui através do grafo, carregando as mensagens, o plano e os resultados.

É o objeto central manipulado por todos os nós e arestas do GraphBuilder.

Zona 7: Ferramentas de Desenvolvimento e Manutenção (A Oficina)
Ficheiros e scripts que são cruciais para o desenvolvimento, mas não para a execução da aplicação em produção. Eles devem ser movidos para uma pasta dev_tools/.

Ficheiro Essencial

Propósito na Nova Arquitetura

scripts/ (diretório)

Contém todos os scripts de pipeline de dados (ETL), limpeza, geração de catálogos, avaliação de agentes

