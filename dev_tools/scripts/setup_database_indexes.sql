-- Script para configurar índices no banco de dados
-- Execute este script no SQL Server Management Studio ou via linha de comando

USE [Projeto_Opcom]
GO

-- Índices para a tabela ADMAT
-- Índice na coluna NOME para buscas por nome de produto
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_ADMAT_NOME' AND object_id = OBJECT_ID('ADMAT'))
BEGIN
    CREATE INDEX IX_ADMAT_NOME ON ADMAT (NOME)
    PRINT 'Índice IX_ADMAT_NOME criado na tabela ADMAT'
END

-- Índice na coluna CÓDIGO para buscas por código de produto
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_ADMAT_CODIGO' AND object_id = OBJECT_ID('ADMAT'))
BEGIN
    CREATE UNIQUE INDEX IX_ADMAT_CODIGO ON ADMAT (CÓDIGO)
    PRINT 'Índice único IX_ADMAT_CODIGO criado na tabela ADMAT'
END

-- Índice composto para buscas por categoria e grupo
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_ADMAT_CATEGORIA_GRUPO' AND object_id = OBJECT_ID('ADMAT'))
BEGIN
    CREATE INDEX IX_ADMAT_CATEGORIA_GRUPO ON ADMAT (CATEGORIA, GRUPO)
    PRINT 'Índice IX_ADMAT_CATEGORIA_GRUPO criado na tabela ADMAT'
END

-- Índices para a tabela Admat_OPCOM
-- Índice na coluna NOME para buscas por nome de produto
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Admat_OPCOM_NOME' AND object_id = OBJECT_ID('Admat_OPCOM'))
BEGIN
    CREATE INDEX IX_Admat_OPCOM_NOME ON Admat_OPCOM (NOME)
    PRINT 'Índice IX_Admat_OPCOM_NOME criado na tabela Admat_OPCOM'
END

-- Índice na coluna CÓDIGO para buscas por código de produto
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Admat_OPCOM_CODIGO' AND object_id = OBJECT_ID('Admat_OPCOM'))
BEGIN
    CREATE UNIQUE INDEX IX_Admat_OPCOM_CODIGO ON Admat_OPCOM (CÓDIGO)
    PRINT 'Índice único IX_Admat_OPCOM_CODIGO criado na tabela Admat_OPCOM'
END

-- Índice composto para buscas por categoria e grupo
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Admat_OPCOM_CATEGORIA_GRUPO' AND object_id = OBJECT_ID('Admat_OPCOM'))
BEGIN
    CREATE INDEX IX_Admat_OPCOM_CATEGORIA_GRUPO ON Admat_OPCOM (CATEGORIA, GRUPO)
    PRINT 'Índice IX_Admat_OPCOM_CATEGORIA_GRUPO criado na tabela Admat_OPCOM'
END

-- Índice para busca por fabricante
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Admat_OPCOM_FABRICANTE' AND object_id = OBJECT_ID('Admat_OPCOM'))
BEGIN
    CREATE INDEX IX_Admat_OPCOM_FABRICANTE ON Admat_OPCOM (FABRICANTE)
    PRINT 'Índice IX_Admat_OPCOM_FABRICANTE criado na tabela Admat_OPCOM'
END

-- Índice para busca por fabricante na tabela ADMAT
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_ADMAT_FABRICANTE' AND object_id = OBJECT_ID('ADMAT'))
BEGIN
    CREATE INDEX IX_ADMAT_FABRICANTE ON ADMAT (FABRICANTE)
    PRINT 'Índice IX_ADMAT_FABRICANTE criado na tabela ADMAT'
END

-- Estatísticas atualizadas para otimizar o plano de execução
UPDATE STATISTICS ADMAT
UPDATE STATISTICS Admat_OPCOM

PRINT 'Índices e estatísticas configurados com sucesso!'
PRINT 'Agora as consultas de produtos devem ser muito mais rápidas.'