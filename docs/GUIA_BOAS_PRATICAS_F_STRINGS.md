# 📚 GUIA DE BOAS PRÁTICAS - Evitar Erros em Prompts e F-Strings

## 🎯 Problema: ValueError em F-Strings com Código Python

### ❌ Erro Comum

```python
# Situação: Gerar prompt para LLM com exemplo de código Python
user_query = "ranking de vendas"

prompt = f"""
Gere um script para: {user_query}

Exemplo:
```python
fig = px.bar(x=dados, labels={{'x': 'Produto', 'y': 'Venda'}})
```
"""
```

**Erro que ocorre:**
```
ValueError: Invalid format specifier ' 'x': 'Produto', 'y': 'Venda'' for object of type 'str'
```

### ✅ Solução Correta

**Opção 1: Escapar com {{ }}** (Recomendado)
```python
prompt = f"""
Gere um script para: {user_query}

Exemplo:
```python
fig = px.bar(x=dados, labels={{'x': 'Produto', 'y': 'Venda'}})
```
"""
```

**Opção 2: Usar String Simples + .format()**
```python
prompt = """
Gere um script para: {query}

Exemplo:
```python
fig = px.bar(x=dados, labels={{'x': 'Produto', 'y': 'Venda'}})
```
""".format(query=user_query)
```

**Opção 3: Concatenação (Menos Pythônico)**
```python
prompt = (
    "Gere um script para: " + user_query + "\n"
    "Exemplo:\n"
    "```python\n"
    "fig = px.bar(x=dados, labels={'x': 'Produto', 'y': 'Venda'})\n"
    "```"
)
```

**Opção 4: Raw String (Para Strings Longas)**
```python
prompt = rf"""
Gere um script para: {user_query}

Exemplo:
```python
fig = px.bar(x=dados, labels={{'x': 'Produto', 'y': 'Venda'}})
```
"""
```

---

## 📋 Checklist: F-Strings com Código Dentro

Antes de usar f-string com código Python como exemplo:

- [ ] Há chaves `{` `}` em dicionários Python no código exemplo?
  - Sim → Use `{{ }}` (escaping duplo)
  - Não → Use f-string normalmente

- [ ] Há variáveis para substituir no prompt?
  - Sim → Use f-string com `{variavel}`
  - Não → Use string simples

- [ ] A string é muito longa (> 10 linhas)?
  - Sim → Considere usar `.format()` para clareza
  - Não → F-string é OK

---

## 🔍 Padrão Seguro para Prompts de LLM

### Template Base (Copiar e Usar)

```python
def gerar_prompt_llm(user_query: str, contexto: dict) -> str:
    """
    Template seguro para gerar prompts com exemplos de código.
    
    Args:
        user_query: Pergunta do usuário
        contexto: Dicionário com variáveis do contexto
    
    Returns:
        String formatada para enviar ao LLM
    """
    
    # Usar f-string para variáveis
    prompt = f"""
    Tarefa: {user_query}
    
    Contexto:
    - Usuário: {contexto.get('user_name', 'Anônimo')}
    - Período: {contexto.get('period', 'Últimos 30 dias')}
    
    Exemplo de resposta (use {{ }} para escapar):
    ```python
    import pandas as pd
    df = pd.read_csv('data.csv')
    # Filtrar por segmento
    df_filtered = df[df['segment'] == 'TECIDOS']
    # Criar gráfico com labels
    labels = {{'x': 'Produto', 'y': 'Vendas'}}
    result = df_filtered.head(10)
    ```
    """
    
    return prompt
```

---

## 🛠️ Ferramentas de Validação

### 1. Verificar Sintaxe Python

```bash
# Verificar arquivo
python -m py_compile seu_arquivo.py

# Verificar com AST
python -c "import ast; ast.parse(open('seu_arquivo.py').read())"
```

### 2. Teste Simples de F-String

```python
# Adicionar ao seu código
try:
    test_prompt = f"""
    Teste: labels={{'x': 'Col1', 'y': 'Col2'}}
    """
    print("✅ F-string OK")
except ValueError as e:
    print(f"❌ Erro na f-string: {e}")
```

### 3. Validação em Testes

```python
import unittest

class TestPrompts(unittest.TestCase):
    def test_prompt_formatting(self):
        """Garantir que prompts com código não têm erro de f-string"""
        user_query = "ranking de vendas"
        
        # Esta função deve não lançar ValueError
        prompt = f"""
        Gere análise para: {user_query}
        Exemplo: labels={{'x': 'A', 'y': 'B'}}
        """
        
        # Se chegou aqui, passou!
        self.assertIn("ranking", prompt)
        self.assertIn("labels=", prompt)
```

---

## 📊 Referência Rápida: Escaping em Diferentes Contextos

| Contexto | Escaping | Exemplo |
|----------|----------|---------|
| F-string normal | Nenhum | `f"{variavel}"` |
| F-string com `{}` no texto | Dobrar | `f"dict={{'key': value}}"` |
| String `.format()` | Dobrar | `"dict={{key: {val}}}".format(val=value)` |
| F-string + regex | Triplo | `f"pattern={{{{{regex_pattern}}}}}"`  |
| Template strings | Nenhum | `Template("dict={key}").substitute(key=value)` |

---

## 🚀 Melhores Práticas em Projetos BI

### ❌ Anti-Padrão
```python
# Ruim: F-string com prompt complexo e código dentro
def gerador_ruim(query, dados):
    prompt = f"""
    Query: {query}
    Código: fig = px.bar(x=df, labels={{'x': 'X', 'y': '{dados}'}})
    """
    return prompt
```

### ✅ Padrão Recomendado
```python
# Bom: Separar template de dados
PROMPT_TEMPLATE = """
Query: {query}

Código de Exemplo:
```python
fig = px.bar(x=df, labels={{'x': 'X', 'y': 'Y'}})
```
"""

def gerador_bom(query, dados):
    return PROMPT_TEMPLATE.format(query=query)
```

---

## 🧪 Testes de Regressão

Adicionar ao seu `pytest`:

```python
# test_agent_prompts.py

import pytest
from core.agents.bi_agent_nodes import generate_plotly_spec

class TestAgentPrompts:
    """Garantir que prompts não têm erro de f-string"""
    
    def test_no_format_specifier_error(self):
        """Testar que generate_plotly_spec não lança ValueError"""
        user_query = "ranking de vendas de tecidos"
        
        try:
            # Chamar função que gera o prompt
            result = generate_plotly_spec(user_query)
            # Se chegou aqui, não teve erro
            assert True
        except ValueError as e:
            if "format specifier" in str(e):
                pytest.fail(f"Format string error detectado: {e}")
            else:
                raise
    
    def test_prompt_contains_escaped_braces(self):
        """Garantir que prompts têm braces escapados"""
        from core.agents.bi_agent_nodes import PROMPT_TEMPLATE
        
        # Contar {{ e }}
        assert PROMPT_TEMPLATE.count("{{") > 0
        assert PROMPT_TEMPLATE.count("}}") > 0
```

---

## 📖 Referências

- **Python F-Strings:** https://docs.python.org/3/tutorial/inputoutput.html#tut-f-strings
- **String Formatting:** https://docs.python.org/3/library/string.html#format-string-syntax
- **LangChain Prompts:** https://python.langchain.com/docs/modules/model_io/prompts/

---

## 💡 Dicas Finais

1. **Sempre testar f-strings com `{}`**: Execute `python -c 'f"{...}"'` antes de commitar
2. **Use type hints**: Ajuda a pegar erros cedo
3. **Logging de prompts**: Registre o prompt gerado para debug
4. **Code review**: Peça review em mudanças de prompt generation
5. **CI/CD**: Adicionar teste de sintaxe ao seu pipeline

---

**Mantido Atualizado**: 2025-12-05  
**Versão**: 1.0  
**Status**: ✅ Aprovado para produção
