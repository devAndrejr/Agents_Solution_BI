# Como Editar o Catálogo de Dados

Este guia explica como refinar o arquivo `CATALOGO_PARA_EDICAO.json` para melhorar a inteligência do agente de BI.

O seu conhecimento do negócio é fundamental para que o agente consiga entender o significado dos dados e responder às perguntas dos usuários com precisão.

## Instruções

1.  **Abra o arquivo `data/CATALOGO_PARA_EDICAO.json`** no seu editor de texto preferido.
2.  Para cada arquivo listado, refine a descrição geral e as descrições de cada coluna.

---

### Exemplo 1: Refinando a Descrição do Arquivo

A descrição do arquivo ajuda o agente a entender o propósito geral do conjunto de dados.

**Antes (Descrição Automática):**
```json
{
    "file_name": "ADMAT.parquet",
    "description": "Dados de Admat."
}
```

**Depois (Editado com Conhecimento do Negócio):**
```json
{
    "file_name": "ADMAT.parquet",
    "description": "Contém o cadastro mestre de todos os produtos (ativos e inativos), incluindo informações de estoque, fornecedor, preços e dados de venda consolidados."
}
```

---

### Exemplo 2: Refinando a Descrição da Coluna

A descrição da coluna é a informação mais importante para o agente. Ela permite que ele relacione a pergunta do usuário ("vendas", "estoque", "preço") com a coluna correta.

**Antes (Descrição Automática):**
```json
"column_descriptions": {
    "VEND_QTD_30D": "Vend qtd 30d",
    "EST_CD": "Est cd"
}
```

**Depois (Editado com Conhecimento do Negócio):**
```json
"column_descriptions": {
    "VEND_QTD_30D": "Total de unidades vendidas do produto nos últimos 30 dias.",
    "EST_CD": "Quantidade de estoque atual disponível no Centro de Distribuição."
}
```

---

Ao salvar suas alterações no arquivo `CATALOGO_PARA_EDICAO.json`, o agente passará a usar este conhecimento para responder às consultas.
