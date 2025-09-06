# Implementação MCP com SQL Server

## Visão Geral

Este documento descreve a implementação do MCP (Multi-Cloud Processing) adaptado para funcionar exclusivamente com SQL Server, sem a necessidade de serviços em nuvem. Esta implementação utiliza recursos nativos do SQL Server como stored procedures, jobs e particionamento de dados para realizar processamento distribuído de consultas.

## Arquitetura

A implementação consiste em três componentes principais:

1. **Adaptador MCP para SQL Server**: Uma camada de abstração que implementa a interface MCP, mas direciona o processamento para o SQL Server local.

2. **Stored Procedures**: Conjunto de procedimentos armazenados no SQL Server que realizam o processamento distribuído das consultas.

3. **Integração com o QueryProcessor**: Modificações no processador de consultas existente para utilizar o adaptador MCP quando apropriado.

## Componentes

### SQLServerMCPAdapter

O adaptador MCP para SQL Server (`sqlserver_adapter.py`) implementa a mesma interface do adaptador MCP original, mas utiliza recursos do SQL Server para processamento. Principais funcionalidades:

- Conexão com o SQL Server usando as configurações existentes
- Processamento de consultas usando stored procedures
- Detecção automática do tipo de consulta (vendas, produtos, categorias)
- Fallback para processamento normal quando necessário

### Stored Procedures

O script `setup_mcp_sqlserver.sql` cria as seguintes stored procedures no SQL Server:

- `sp_mcp_process_query`: Procedimento principal que analisa a consulta e direciona para o procedimento específico
- `sp_mcp_get_sales_data`: Processa consultas relacionadas a vendas
- `sp_mcp_get_product_data`: Processa consultas relacionadas a produtos
- `sp_mcp_get_category_data`: Processa consultas relacionadas a categorias

## Configuração

### Pré-requisitos

- SQL Server instalado e configurado
- Acesso administrativo ao banco de dados
- Dependências Python: pyodbc, pandas

### Passos para Instalação

1. Execute o script `setup_mcp_sqlserver.sql` no SQL Server para criar as stored procedures necessárias:

```sql
-- Substitua [seu_banco_de_dados] pelo nome do seu banco de dados
USE [seu_banco_de_dados];
GO
-- Execute o resto do script
```

2. Verifique se o arquivo de configuração `data/sqlserver_mcp_config.json` foi criado automaticamente. Se não, crie-o manualmente com o seguinte conteúdo:

```json
{
    "connection": {
        "server": "seu_servidor",
        "database": "seu_banco_de_dados",
        "username": "seu_usuario",
        "password": "sua_senha",
        "driver": "ODBC Driver 17 for SQL Server",
        "trust_server_certificate": "yes"
    },
    "processing": {
        "max_parallel_queries": 4,
        "timeout_seconds": 30,
        "use_stored_procedures": true,
        "use_partitioning": true
    },
    "stored_procedures": {
        "process_query": "sp_mcp_process_query",
        "get_sales_data": "sp_mcp_get_sales_data",
        "get_product_data": "sp_mcp_get_product_data",
        "get_category_data": "sp_mcp_get_category_data"
    }
}
```

## Uso

O sistema automaticamente detecta quando usar o processamento MCP baseado no SQL Server. Consultas complexas que se beneficiam do processamento distribuído serão automaticamente direcionadas para o adaptador MCP.

Exemplos de consultas que usarão o MCP:

- "Mostre as vendas por período dos últimos 3 meses"
- "Qual o comparativo de vendas entre categorias?"
- "Gere um relatório completo de vendas por produto"
- "Quais são os top 10 produtos mais vendidos?"

## Personalização

### Ajustando os Critérios de Seleção MCP

Você pode ajustar quando o sistema deve usar o MCP modificando o método `_should_use_mcp` no arquivo `query_processor.py`. Adicione ou remova padrões de expressão regular conforme necessário.

### Adicionando Novas Stored Procedures

Para adicionar novas capacidades de processamento:

1. Crie uma nova stored procedure no SQL Server
2. Adicione a referência à stored procedure no arquivo de configuração
3. Atualize o adaptador MCP para utilizar a nova stored procedure

## Solução de Problemas

### Logs

Os logs do adaptador MCP para SQL Server são armazenados em `logs/mcp_sqlserver.log`. Consulte este arquivo para diagnosticar problemas.

### Problemas Comuns

1. **Erro de conexão com o SQL Server**:
   - Verifique as configurações de conexão no arquivo `data/sqlserver_mcp_config.json`
   - Confirme que o SQL Server está em execução e acessível

2. **Stored Procedures não encontradas**:
   - Execute novamente o script `setup_mcp_sqlserver.sql`
   - Verifique se o banco de dados correto está sendo usado

3. **Erro no processamento de consultas**:
   - Verifique os logs para identificar o erro específico
   - O sistema automaticamente fará fallback para o processamento normal em caso de erro

## Considerações de Desempenho

Para obter o melhor desempenho do MCP com SQL Server:

1. **Índices**: Crie índices apropriados nas tabelas de vendas, produtos e categorias
2. **Particionamento**: Para grandes volumes de dados, considere particionar as tabelas por data ou categoria
3. **Recursos do Servidor**: Ajuste a configuração `max_parallel_queries` de acordo com os recursos disponíveis no servidor

## Limitações

- O desempenho depende dos recursos disponíveis no servidor SQL Server
- Consultas muito complexas podem não ser otimizadas automaticamente
- O particionamento de dados requer configuração adicional no SQL Server

# Integração MCP com SQL Server

## Configuração
- Defina as variáveis no `.env`:
  - MSSQL_SERVER, MSSQL_DATABASE, MSSQL_USER, MSSQL_PASSWORD, DB_DRIVER
- Use ODBC Driver 17 ou 18 for SQL Server

## Fluxo de Dados
- API → MCP → SQL Server
- Todas as queries REST passam pelo MCP

## Troubleshooting
- Verifique drivers, porta, serviço e variáveis
- Use scripts de diagnóstico para checar ambiente
- Consulte logs para detalhes de erro

## Segurança
- Nunca versionar credenciais reais
- Use variáveis de ambiente para segredos
- Restrinja acesso ao banco por IP