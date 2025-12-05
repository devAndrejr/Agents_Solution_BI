# 🔐 Guia Rápido - Autenticação Code Chat

## 📋 Resumo

O **Code Chat** agora é acessível **APENAS para administradores** com autenticação obrigatória.

**Credenciais Padrão:**
- Usuário: `admin`
- Senha: `admin123`

⚠️ **Altere imediatamente em produção!**

---

## 🚀 Como Usar

### 1️⃣ Iniciar a Aplicação
```bash
streamlit run streamlit_app.py
```

### 2️⃣ Acessar Code Chat
```
http://localhost:8501 → Sidebar → 💻 Code Chat
```

### 3️⃣ Fazer Login
- **Usuário:** `admin`
- **Senha:** `admin123`
- **Botão:** 🔓 Fazer Login

### 4️⃣ Usar o Code Chat
- Pergunte sobre seu código
- Solicite correções e refatorações
- Explore a estrutura do projeto

### 5️⃣ Fazer Logout
- Clique no botão **🚪 Logout** no sidebar

---

## 🔑 Alterar Senha do Admin

### Opção 1: PowerShell (Temporário)
```powershell
$env:ADMIN_PASSWORD='sua-nova-senha-super-segura'
streamlit run streamlit_app.py
```

### Opção 2: Arquivo `.env` (Permanente)
Crie ou edite o arquivo `.env`:
```
GEMINI_API_KEY=sua-chave-gemini
ADMIN_PASSWORD=sua-nova-senha-super-segura
```

### Opção 3: Variável de Sistema Windows (Permanente)
1. Abra **Painel de Controle** → **Sistema** → **Variáveis de Ambiente**
2. Clique em **Nova** e adicione:
   - **Nome:** `ADMIN_PASSWORD`
   - **Valor:** `sua-nova-senha-super-segura`
3. Reinicie o PowerShell/Streamlit

---

## 🛡️ Segurança

### ✅ Recursos Implementados
- **Hashing SHA256:** Senhas nunca em texto plano
- **Brute Force Protection:** Máximo 5 tentativas
- **st.stop():** Acesso bloqueado sem autenticação
- **Variáveis de Ambiente:** Senhas seguras, não no código
- **Logout Seguro:** Limpa session_state completamente

### 🔒 Verificação Precoce
A autenticação é verificada ANTES de qualquer outra código executar.

---

## 📊 Fluxo de Autenticação

```
Acessa Code Chat
       ↓
Verifica: is_authenticated()?
       ↓
   SIM → Acesso ao Code Chat
   NÃO ↓
    Mostra Tela de Login
       ↓
   Insere credenciais
       ↓
   Valida: username + password hash
       ↓
   SIM → Permite acesso
   NÃO ↓
    Incrementa tentativas
   (Máximo 5 tentativas)
```

---

## 💡 Exemplos

### Cenário 1: Primeiro Login
```
1. Acessa: Code Chat
2. Tela: Login aparece
3. Insere: admin / admin123
4. Resultado: ✅ Acesso ao Code Chat
```

### Cenário 2: Senha Errada
```
1. Insere: admin / senhaerrada
2. Mensagem: ❌ Credenciais inválidas. Tentativas: 4
3. Tenta novamente
```

### Cenário 3: Muitas Tentativas
```
1. Após 5 tentativas falhas
2. Mensagem: ❌ Muitas tentativas. Tente novamente em 1 hora
3. Deve reiniciar Streamlit para resetar
```

### Cenário 4: Logout
```
1. Sidebar: 🚪 Logout
2. Click: Volta para tela de login
3. Pronto: Novo login necessário
```

---

## 🔧 Implementação Técnica

### Arquivo: `core/auth_code_chat.py`
Módulo com funções:
- `initialize_auth_state()` - Inicializa variáveis
- `is_authenticated()` - Verifica autenticação
- `login_admin()` - Realiza login
- `logout_admin()` - Realiza logout
- `hash_password()` - Hash SHA256
- `verify_password()` - Verifica credenciais
- `show_login_page()` - UI de login

### Arquivo: `pages/1_💻_Code_Chat.py`
Atualizado para:
1. Importar módulo de autenticação
2. Verificar autenticação PRIMEIRO
3. `st.stop()` se não autenticado
4. Mostrar botão de logout

### Variáveis de Ambiente
- `ADMIN_PASSWORD` - Senha do admin (padrão: `admin123`)
- `GEMINI_API_KEY` - Chave da API Gemini (obrigatória)

---

## 🚨 Troubleshooting

### Problema: "Módulo de autenticação não encontrado"
**Solução:** Verifique se `core/auth_code_chat.py` existe

### Problema: "Muitas tentativas"
**Solução:** Reinicie Streamlit para resetar o contador

### Problema: "Senha incorreta"
**Solução:** Verifique a variável `ADMIN_PASSWORD` configurada

### Problema: "GEMINI_API_KEY não encontrada"
**Solução:** Configure a chave no `.env` ou como variável de ambiente

---

## 📚 Próximas Melhorias

- [ ] Banco de dados de usuários
- [ ] Múltiplos níveis de permissão (admin, editor, viewer)
- [ ] Auditoria de logs
- [ ] 2FA (Two-Factor Authentication)
- [ ] LDAP/Active Directory
- [ ] Expiração de sessão
- [ ] Recuperação de senha

---

## ✅ Checklist para Produção

- [ ] Alterar `ADMIN_PASSWORD` de `admin123`
- [ ] Usar senha forte (12+ caracteres, mix de maiúsculas, minúsculas, números, símbolos)
- [ ] Configurar em variável de ambiente, não no código
- [ ] Testar login com nova senha
- [ ] Testar logout
- [ ] Verificar que acesso não autorizado é bloqueado
- [ ] Documentar credenciais em lugar seguro
- [ ] Configurar HTTPS em produção

---

**Status:** ✅ **Autenticação Ativa**  
**Último Update:** 05/12/2024  
**Versão:** 1.0.2
