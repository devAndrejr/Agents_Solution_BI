# PROMPT DE ORIENTAÇÃO PARA ANÁLISE DE PROJETO

### 1. PERSONA E PAPEL
**QUEM VOCÊ É:**
Você é um híbrido de Arquiteto de Soluções e Gerente de Produto Sênior, com mais de 15 anos de experiência na construção de plataformas de dados e produtos de B.I. conversacional. Sua especialidade é analisar Documentos de Requisitos de Produto (PRDs) para identificar riscos técnicos e de produto, definir arquiteturas robustas e criar estratégias de implementação que garantam o sucesso do projeto. Você é pragmático, detalhista e focado em resolver os desafios mais complexos de interação humano-computador.

---

### 2. CONTEXTO E OBJETIVO GERAL
**A SITUAÇÃO ATUAL:**
Eu sou o líder técnico do projeto **Agent_BI**. Nós temos um PRD detalhado que descreve a visão e os requisitos do produto. Embora a visão geral seja clara, estou enfrentando um desafio crítico e específico: **a dificuldade em fazer o agente gerar e apresentar gráficos de forma eficaz na interface de conversação.** As respostas gráficas não estão sendo intuitivas, e a transição da conversa para a visualização é problemática.

**MEU OBJETIVO FINAL:**
Obter um relatório de análise estratégica e técnica sobre todo o projeto descrito no PRD. Este relatório deve ser profundo, usando técnicas avançadas de análise de sistemas para garantir que a arquitetura e o design do produto sejam robustos. O foco principal do relatório deve ser fornecer uma solução clara e detalhada para o problema da geração de gráficos na interface.

---

### 3. TAREFA ESPECÍFICA E IMEDIATA
**SUA TAREFA AGORA:**
Analise profundamente o Documento de Requisitos do Produto (PRD) do 'Agent_BI' que fornecerei no final deste prompt. Com base na sua análise, gere um relatório robusto e detalhado, estruturado nas seguintes seções:

1.  **Análise Geral do Produto:** Uma avaliação crítica da visão, metas e público-alvo. Destaque os pontos fortes e as potenciais fraquezas da proposta de valor.

2.  **Análise de Riscos e Pontos de Atenção:** Identifique os 5 principais riscos do projeto, abrangendo áreas como técnica (escalabilidade, performance), dados (precisão, governança), experiência do usuário (adoção, usabilidade) e negócio (atingimento das metas).

3.  **[SEÇÃO CRÍTICA] Estratégia de Implementação para Gráficos Conversacionais:** Esta é a seção mais importante. Detalhe uma estratégia completa para resolver o desafio da geração de gráficos. Aborde os seguintes pontos:
    * **Fluxo de Experiência do Usuário (UX Flow):** Descreva o passo a passo ideal. Como o usuário pede um gráfico? O agente faz perguntas de esclarecimento (ex: "Qual tipo de gráfico você prefere?")? O gráfico aparece diretamente no chat ou em um modal? O que acontece depois que o gráfico é exibido?
    * **Arquitetura Técnica para Geração de Gráficos:** Proponha uma arquitetura de backend e frontend. O agente deve gerar uma imagem estática (ex: com Matplotlib/Seaborn) ou uma especificação para um gráfico interativo (ex: JSON para Plotly, Chart.js, ou Vega-Lite)? Discuta os prós e contras.
    * **Modelo de Interação (Estático vs. Interativo):** Analise a trade-off entre enviar uma imagem (`.png`) do gráfico no chat versus incorporar um componente de gráfico interativo. Como a Feature 4.2.3 (Interatividade) se aplica aqui? A resposta deve ser um link para um dashboard completo ou o gráfico deve ser explorável na própria conversa?
    * **Tratamento de Ambiguidade e Desambiguação:** Como o sistema deve reagir a pedidos vagos como "me mostre as vendas"? Detalhe uma estratégia para o agente pedir esclarecimentos ("Vendas por região ou por produto?", "Em qual período?") antes de tentar gerar um gráfico.

4.  **Recomendações Técnicas e de Arquitetura:** Forneça recomendações para a pilha de tecnologia (stack). Sugira abordagens para garantir os requisitos não-funcionais, como performance (cache de consultas), escalabilidade (arquitetura de microsserviços?) e segurança (RBAC).

5.  **Plano de Ação Sugerido (Roadmap Simplificado):** Proponha um roadmap de implementação em 3 fases (ex: MVP, Versão 1.0, Pós-Lançamento), priorizando as funcionalidades do PRD para entregar valor mais rápido e mitigar os maiores riscos primeiro.

---

### 4. REGRAS E RESTRIÇÕES
- Toda a sua análise deve ser baseada **exclusivamente** nas informações contidas no PRD abaixo. Não invente funcionalidades.
- Seja crítico e proativo. Não se limite a resumir o documento; seu valor está em identificar problemas ocultos e propor soluções concretas.
- O tom deve ser profissional, consultivo e técnico.
- Formate sua resposta final usando Markdown para garantir a legibilidade (títulos, subtítulos, listas, negrito).
- **Certificação de Implementação:** Para cada recomendação técnica, de arquitetura ou de implementação que você fizer, você deve "certificá-la". Isso significa que você precisa fornecer uma justificativa clara, explicando o porquê da sua escolha, apresentando os trade-offs (prós e contras de outras abordagens que foram consideradas e descartadas) e citando como sua sugestão se alinha com os requisitos funcionais e não-funcionais descritos no PRD (como escalabilidade, segurança e performance).

---

### 5. DOCUMENTO PARA ANÁLISE (PRD)

# Documento de Requisitos do Produto (PRD): Agent_BI

**Autor:** Gemini
**Versão:** 1.0
**Data:** 2025-09-08

---

## 1. Introdução

### 1.1. Propósito
Este documento descreve os requisitos, funcionalidades e o propósito do **Agent_BI**, uma plataforma de Business Intelligence conversacional. O objetivo é fornecer uma fonte central de verdade para as equipes de desenvolvimento, design, e de negócios para alinhar a visão e o escopo do produto.

### 1.2. Problema a ser Resolvido
Empresas coletam grandes volumes de dados, mas extrair insights acionáveis de forma rápida e intuitiva ainda é um desafio. Analistas de negócios e tomadores de decisão frequentemente dependem de equipes técnicas para criar relatórios e dashboards, gerando um processo lento e pouco flexível. O Agent_BI visa democratizar o acesso aos dados, permitindo que usuários de negócio obtenham respostas e visualizações através de linguagem natural.

### 1.3. Público-Alvo
*   **Diretores e Gestores:** Precisam de uma visão consolidada e de alto nível dos KPIs para tomar decisões estratégicas.
*   **Analistas de Negócios:** Necessitam de uma ferramenta para explorar dados, validar hipóteses e criar relatórios detalhados sem depender de SQL ou código.
*   **Compradores e Equipes de Operações:** Precisam de acesso a dados específicos de suas áreas (ex: performance de produtos, níveis de estoque) para otimizar suas rotinas.
*   **Administradores de Sistema:** Responsáveis por gerenciar o acesso, a segurança e a integridade dos dados na plataforma.

---

## 2. Visão Geral e Metas

### 2.1. Visão do Produto
Ser a principal interface de interação com dados da empresa, transformando a maneira como os colaboradores acessam e interpretam informações de negócio, tornando o processo tão simples quanto conversar com um especialista.

### 2.2. Metas de Negócio
*   **Reduzir em 40%** o tempo gasto por analistas na geração de relatórios recorrentes.
*   **Aumentar em 25%** a velocidade na tomada de decisões baseadas em dados.
*   **Capacitar 90%** dos gestores a consultarem dados de forma autônoma.

### 2.3. Metas do Produto
*   Fornecer respostas a consultas em linguagem natural com mais de 95% de precisão.
*   Garantir que o tempo de carregamento dos dashboards interativos não exceda 5 segundos.
*   Manter um uptime de serviço de 99.9%.

---

## 3. Personas de Usuário

*   **Carlos, o Diretor de Vendas:** "Preciso saber o faturamento total do último trimestre, comparado com o mesmo período do ano anterior, e quero ver isso em um gráfico de barras. Não tenho tempo para esperar um relatório."
*   **Ana, a Analista de Marketing:** "Quero entender a correlação entre o investimento em campanhas de marketing digital e o volume de vendas por região. Preciso cruzar dados de diferentes fontes e explorar as tendências."
*   **Beatriz, a Compradora:** "Necessito de uma lista dos 10 produtos com menor giro de estoque nos últimos 30 dias para planejar uma ação de queima de estoque."

---

## 4. Requisitos e Funcionalidades (Features)

### 4.1. Epic: Interface Conversacional (Agente)
*   **Feature 4.1.1: Processamento de Linguagem Natural (PLN):** O sistema deve ser capaz de interpretar perguntas complexas feitas em português.
*   **Feature 4.1.2: Geração de Respostas:** O agente deve responder com textos, números, e também sugerir ou gerar visualizações (gráficos, tabelas).
*   **Feature 4.1.3: Histórico de Conversas:** O usuário deve poder ver suas conversas anteriores com o agente.

### 4.2. Epic: Dashboards e Visualizações
*   **Feature 4.2.1: Dashboard Principal:** Uma visão geral com os principais KPIs da empresa.
*   **Feature 4.2.2: Geração Dinâmica de Gráficos:** O sistema deve gerar gráficos (barras, linhas, pizza, etc.) com base nas solicitações do usuário.
*   **Feature 4.2.3: Interatividade:** Os usuários devem poder filtrar, ordenar e explorar os dados diretamente nos dashboards e gráficos.

### 4.3. Epic: Gestão de Dados e Catálogo
*   **Feature 4.3.1: Monitoramento de Pipeline:** Uma interface para administradores acompanharem a saúde das integrações e atualizações de dados.
*   **Feature 4.3.2: Gerenciamento de Catálogo de Dados:** Uma área para administradores editarem, enriquecerem e aprovarem os metadados que o agente utiliza para entender o contexto do negócio.

### 4.4. Epic: Administração e Segurança
*   **Feature 4.4.1: Autenticação de Usuários:** O acesso ao sistema deve ser protegido por login e senha.
*   **Feature 4.4.2: Controle de Acesso Baseado em Perfil (RBAC):** Diferentes perfis de usuário (admin, gestor, comprador) devem ter acesso a diferentes funcionalidades e conjuntos de dados.
*   **Feature 4.4.3: Painel de Administração:** Interface para gerenciar usuários, perfis de acesso e configurações gerais do sistema.

---

## 5. Requisitos Não-Funcionais

*   **Desempenho:** Consultas simples devem ser respondidas em menos de 3 segundos. A geração de dashboards complexos não deve exceder 10 segundos.
*   **Escalabilidade:** A arquitetura deve suportar um aumento de 50% no número de usuários e 100% no volume de dados nos próximos 12 meses sem degradação de performance.
*   **Segurança:** Todos os dados sensíveis devem ser criptografados em trânsito e em repouso. O sistema deve estar protegido contra as 10 principais vulnerabilidades da OWASP.
*   **Usabilidade:** A interface deve ser intuitiva e acessível, exigindo o mínimo de treinamento para novos usuários.
*   **Confiabilidade:** O sistema deve ter um uptime de 99.9% e possuir mecanismos robustos de logging e monitoramento de erros.

---

## 6. Fora do Escopo (Versão 1.0)

*   Aplicativo móvel nativo.
*   Integração com fontes de dados em tempo real (streaming).
*   Funcionalidades de análise preditiva ou Machine Learning avançado.
*   Suporte a múltiplos idiomas (além do português).

---

## 7. Métricas de Sucesso

*   **Engajamento:** Número de usuários ativos diários/mensais (DAU/MAU).
*   **Adoção:** Percentual do público-alvo que utiliza a ferramenta ativamente após 3 meses do lançamento.
*   **Satisfação do Usuário:** Pesquisas de Net Promoter Score (NPS) ou CSAT.
*   **Performance do Agente:** Taxa de sucesso nas respostas a perguntas (consultas respondidas corretamente / total de consultas).

---

## 8. Anexos e Referências

*   **Link para o Protótipo de UI/UX:** (se aplicável)
*   **Documento de Arquitetura Técnica:** (se aplicável)
