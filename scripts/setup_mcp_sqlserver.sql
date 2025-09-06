
-- Script MCP SQL Server Corrigido com base nas colunas reais

-- Procedure para processar consultas genéricas (stub)
IF OBJECT_ID('dbo.sp_mcp_process_query', 'P') IS NULL
BEGIN
    EXEC('
    CREATE PROCEDURE dbo.sp_mcp_process_query
        @query_text NVARCHAR(MAX)
    AS
    BEGIN
        SET NOCOUNT ON;
        -- Esta é uma implementação de stub.
        -- Em uma implementação real, esta SP rotearia a consulta para outras SPs
        -- ou executaria lógica de processamento de consulta complexa.

        DECLARE @product_code NVARCHAR(50);

        -- Tenta extrair o código do produto da query_text
        IF @query_text LIKE CHAR(37) + ''produto'' + CHAR(37)
        BEGIN
            -- Converte a consulta para minúsculas para facilitar a busca
            DECLARE @query_lower NVARCHAR(MAX) = LOWER(@query_text);

            -- Encontra a posição da palavra ''produto'' na consulta
            DECLARE @pos INT = CHARINDEX(''produto'', @query_lower);

            -- Extrai a parte da string após a palavra ''produto''
            DECLARE @rest NVARCHAR(MAX) = SUBSTRING(@query_lower, @pos + 7, LEN(@query_lower));

            -- Remove caracteres não numéricos
            DECLARE @clean_rest NVARCHAR(MAX) = '''';
            DECLARE @j INT = 1;
            DECLARE @rest_len INT = LEN(@rest);

            WHILE @j <= @rest_len
            BEGIN
                DECLARE @current_char NCHAR(1) = SUBSTRING(@rest, @j, 1);
                IF @current_char BETWEEN ''0'' AND ''9''
                    SET @clean_rest = @clean_rest + @current_char;
                SET @j = @j + 1;
            END;

            -- Extrai apenas os dígitos do início da string limpa
            IF LEN(@clean_rest) > 0
                SET @product_code = @clean_rest;
        END

        IF @product_code IS NOT NULL
        BEGIN
            EXEC dbo.sp_mcp_get_product_data @product_code = @product_code;
        END
        ELSE
        BEGIN
            SELECT ''Consulta processada com sucesso (stub)'' AS Resultado, @query_text AS QueryRecebida;
        END
    END
    ')
END
GO

-- Procedure para obter dados de vendas (exemplo)
IF OBJECT_ID('dbo.sp_mcp_get_sales_data', 'P') IS NULL
BEGIN
    EXEC('
    CREATE PROCEDURE dbo.sp_mcp_get_sales_data
    AS
    BEGIN
        SET NOCOUNT ON;
        -- Exemplo de dados de vendas. Adapte conforme a estrutura real da sua tabela de vendas.
        SELECT TOP 10
            [CÓDIGO] AS ProductCode,
            [NOME] AS ProductName,
            TRY_CAST([VENDA 30D] AS FLOAT) AS SalesLast30Days,
            [CATEGORIA] AS Category
        FROM [dbo].[Admat_OPCOM]
        WHERE TRY_CAST([VENDA 30D] AS FLOAT) IS NOT NULL
        ORDER BY SalesLast30Days DESC;
    END
    ')
END
GO

-- Procedure para dados de produtos
IF OBJECT_ID('dbo.sp_mcp_get_product_data', 'P') IS NULL
BEGIN
    EXEC('
    CREATE PROCEDURE dbo.sp_mcp_get_product_data
    @product_code NVARCHAR(50) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    IF @product_code IS NULL
    BEGIN
        -- Se nenhum código específico for fornecido, retorna os top 100 produtos
        SELECT TOP 100
            [CÓDIGO] AS Codigo,
            [NOME] AS Nome,
            [PREÇO 38%] AS Preco38,
            [EST# UNE] AS Estoque,
            [FABRICANTE] AS Fabricante
        FROM [dbo].[Admat_OPCOM]
        WHERE ([PREÇO 38%] IS NOT NULL)
    END
    ELSE
    BEGIN
        -- Se um código específico for fornecido, retorna apenas esse produto
        SELECT
            [CÓDIGO] AS Codigo,
            [NOME] AS Nome,
            [PREÇO 38%] AS Preco38,
            [EST# UNE] AS Estoque,
            [FABRICANTE] AS Fabricante
        FROM [dbo].[Admat_OPCOM]
        WHERE [CÓDIGO] = @product_code
    END
    END
    ')
END
GO

-- Procedure para dados de vendas agregadas por categoria
IF OBJECT_ID('dbo.sp_mcp_get_category_data', 'P') IS NULL
BEGIN
    EXEC('
    CREATE PROCEDURE dbo.sp_mcp_get_category_data
    AS
    BEGIN
        SET NOCOUNT ON;
        SELECT
            [CATEGORIA],
            COUNT([CÓDIGO]) AS QuantidadeProdutos,
            SUM(TRY_CAST([VENDA 30D] AS FLOAT)) AS TotalVendido
        FROM [dbo].[Admat_OPCOM]
        GROUP BY [CATEGORIA]
    END
    ')
END
GO

PRINT 'Configuração do MCP para SQL Server corrigida com sucesso!';
