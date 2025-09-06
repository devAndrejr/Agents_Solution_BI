import logging
import os
import re
import uuid
from functools import wraps

import bleach
# import spacy
# from spacy.matcher import PhraseMatcher
import openai
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_cors import CORS
from werkzeug.utils import secure_filename

from core.utils.db_utils import get_table_df

# Configuração de logging
logger = logging.getLogger(__name__)

frontend = Blueprint("frontend", __name__)

UPLOAD_FOLDER = "data/input"
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}

# Carregar modelo spaCy para classificação de intents
# nlp = spacy.blank("pt")

# Exemplos de intents
INTENT_PATTERNS = {
    "consulta_dados": [
        "vendas por mês",
        "total de clientes",
        "faturamento do último trimestre",
        "clientes ativos",
        "produtos por categoria",
        "total de produtos",
        "categoria",
        "mostre o total",
    ],
    "pergunta_aberta": [
        "explique",
        "como posso",
        "o que significa",
        "me explique",
    ],
    "pergunta_hibrida": [
        "compare vendas",
        "compare o faturamento",
        "explique a diferença",
    ],
    "arquivo": ["arquivo que enviei", "dados enviados", "coluna do arquivo"],
}

# matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
# for intent, patterns in INTENT_PATTERNS.items():
#     matcher.add(intent, [nlp.make_doc(p) for p in patterns])


def classificar_intent(texto):
    # doc = nlp(texto)
    # matches = matcher(doc)
    # if not matches:
    #     return "pergunta_aberta"  # fallback para OpenAI
    # match_id, start, end = matches[0]
    # intent = nlp.vocab.strings[match_id]
    # return intent
    return "pergunta_aberta"


# Função para consultar OpenAI
OPENAI_MODEL = "gpt-3.5-turbo"


def consultar_openai(prompt):
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        if (
            response.choices
            and response.choices[0].message
            and response.choices[0].message.content
        ):
            return response.choices[0].message.content.strip()
        return ""
    except Exception as e:
        logger.error(f"Erro ao consultar OpenAI: {e}")
        return "Desculpe, houve um erro ao consultar a IA."


# ===== DECORADORES DE SEGURANÇA =====
def login_required(f):
    """Decorator para verificar se o usuário está autenticado"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash("Por favor, faça login para acessar esta página.", "warning")
            return redirect(url_for("frontend.login_route"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Decorator para verificar se o usuário é admin"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash("Por favor, faça login para acessar esta página.", "warning")
            return redirect(url_for("frontend.login_route"))

        user = get_user()
        if not user.get("is_admin"):
            flash(
                "Acesso negado. Você não tem permissão para acessar esta página.",
                "danger",
            )
            return redirect(url_for("frontend.dashboard"))

        return f(*args, **kwargs)

    return decorated_function


# ===== FUNÇÕES AUXILIARES =====
def is_authenticated():
    """Verifica se o usuário está autenticado"""
    return session.get("user_id") is not None


def get_user():
    """Retorna dados do usuário da sessão"""
    return {
        "id": session.get("user_id"),
        "nome": session.get("user_nome", "Usuário"),
        "email": session.get("user_email", "user@email.com"),
        "is_admin": session.get("is_admin", False),
    }


def sanitize_input(text):
    """Sanitiza entrada do usuário para prevenir XSS"""
    if not text:
        return ""
    # Limpa HTML/JS com bleach
    sanitized = bleach.clean(text, tags=[], attributes={}, strip=True)
    # Remove caracteres perigosos adicionais
    dangerous_chars = ["<", ">", "{", "}", "script", "javascript"]
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    return sanitized.strip()


def validate_email(email):
    """Valida formato de email"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


# ===== ROTAS =====
@frontend.route("/")
def root():
    """Rota raiz - redireciona para dashboard ou login"""
    if is_authenticated():
        return redirect(url_for("frontend.dashboard"))
    return redirect(url_for("frontend.login_route"))


@frontend.route("/login", methods=["GET", "POST"])
def login_route():
    """Rota de login"""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Validação básica
        if not email or not password:
            flash("Por favor, preencha todos os campos.", "warning")
            return render_template("login.html", error="Campos obrigatórios")

        if not validate_email(email):
            flash("Por favor, insira um email válido.", "warning")
            return render_template("login.html", error="Email inválido")

        # TODO: Implementar autenticação real
        # Por enquanto, simula login bem-sucedido
        if email == "admin@caculinha.com" and password == "admin123":
            session["user_id"] = 1
            session["user_nome"] = "Administrador"
            session["user_email"] = email
            session["is_admin"] = True
            logger.info(f"Login bem-sucedido para: {email}")
            return redirect(url_for("frontend.dashboard"))
        else:
            flash("Email ou senha incorretos.", "danger")
            logger.warning(f"Tentativa de login falhou para: {email}")
            return render_template("login.html", error="Credenciais inválidas")

    return render_template("login.html", error=None)


@frontend.route("/dashboard")
@login_required
def dashboard():
    """Dashboard principal"""
    try:
        user = get_user()
        return render_template(
            "index.html",
            user=user,
            active_page="dashboard",
        )
    except Exception as e:
        logger.error(f"Erro ao carregar dashboard: {e}")
        flash("Erro ao carregar o dashboard. Tente novamente.", "danger")
        return redirect(url_for("frontend.login_route"))


@frontend.route("/chat", methods=["GET"])
@login_required
def chat():
    """Página de chat/consultas (moderna)"""
    user = get_user()
    return render_template("chat_moderno.html", user=user, active_page="chat")


@frontend.route("/exemplos-visuais")
@login_required
def exemplos_visuais():
    """Página com exemplos visuais dos estilos de chatbot"""
    return render_template("exemplos_visuais.html")


@frontend.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    """Página de perfil do usuário"""
    try:
        user = get_user()
        error = None
        success = None

        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            email = request.form.get("email", "").strip()

            # Validações
            if not nome or not email:
                error = "Nome e email são obrigatórios."
            elif not validate_email(email):
                error = "Email inválido."
            elif len(nome) < 2:
                error = "Nome deve ter pelo menos 2 caracteres."
            elif len(nome) > 100:
                error = "Nome deve ter no máximo 100 caracteres."
            else:
                # TODO: Implementar atualização real do perfil
                success = "Perfil atualizado com sucesso!"
                session["user_nome"] = nome
                session["user_email"] = email
                logger.info(f'Perfil atualizado para usuário {user["id"]}')

        return render_template(
            "perfil.html",
            user=user,
            active_page="perfil",
            error=error,
            success=success,
        )

    except Exception as e:
        logger.error(f"Erro na página de perfil: {e}")
        flash("Erro ao carregar perfil. Tente novamente.", "danger")
        return redirect(url_for("frontend.dashboard"))


@frontend.route("/monitoramento")
@admin_required
def monitoramento():
    """Página de monitoramento (apenas admin)"""
    try:
        user = get_user()
        return render_template(
            "index.html",
            user=user,
            active_page="monitoramento",
        )
    except Exception as e:
        logger.error(f"Erro na página de monitoramento: {e}")
        flash("Erro ao carregar monitoramento.", "danger")
        return redirect(url_for("frontend.dashboard"))


@frontend.route("/logs")
@admin_required
def logs():
    """Página de logs (apenas admin)"""
    try:
        user = get_user()
        return render_template(
            "index.html",
            user=user,
            active_page="logs",
        )
    except Exception as e:
        logger.error(f"Erro na página de logs: {e}")
        flash("Erro ao carregar logs.", "danger")
        return redirect(url_for("frontend.dashboard"))


@frontend.route("/usuarios")
@admin_required
def usuarios():
    """Página de gerenciamento de usuários (apenas admin)"""
    try:
        user = get_user()
        return render_template(
            "index.html",
            user=user,
            active_page="usuarios",
        )
    except Exception as e:
        logger.error(f"Erro na página de usuários: {e}")
        flash("Erro ao carregar usuários.", "danger")
        return redirect(url_for("frontend.dashboard"))


@frontend.route("/logout")
def logout():
    """Logout do usuário"""
    try:
        user_id = session.get("user_id")
        if user_id:
            logger.info(f"Logout do usuário {user_id}")

        session.clear()
        flash("Logout realizado com sucesso.", "success")
    except Exception as e:
        logger.error(f"Erro no logout: {e}")

    return redirect(url_for("frontend.login_route"))


# ===== ROTAS DE API PARA AJAX =====
@frontend.route("/api/chat/send", methods=["POST"])
# @limiter.limit("30/minute")
@login_required
def api_chat_send():
    """
    Envia uma mensagem para o chatbot e recebe resposta (OpenAI, SQL ou análise de arquivo).
    ---
    tags:
      - Chat
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Me mostre o total de produtos por categoria"
    responses:
      200:
        description: Resposta do chatbot
        schema:
          type: object
          properties:
            success:
              type: boolean
            response:
              type: string
            plotly_data:
              type: object
              description: Dados para gráfico Plotly (opcional)
            error:
              type: string
              nullable: true
      400:
        description: Erro de validação
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    try:
        logger.info("Recebida requisição em /api/chat/send")
        logger.info(f"Sessão atual: {dict(session)}")
        logger.info(f"Cookies recebidos: {request.cookies}")
        data = request.get_json()
        logger.info(f"Dados recebidos: {data}")
        if not data or "message" not in data:
            logger.warning("Mensagem não fornecida")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Mensagem não fornecida",
                    }
                ),
                400,
            )

        message = data["message"].strip()
        logger.info(f"Mensagem recebida: {message}")

        # Validações
        if not message:
            logger.warning("Mensagem vazia")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Mensagem não pode estar vazia",
                    }
                ),
                400,
            )
        if len(message) < 3:
            logger.warning("Mensagem muito curta")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Mensagem deve ter pelo menos 3 caracteres",
                    }
                ),
                400,
            )
        if len(message) > 500:
            logger.warning("Mensagem muito longa")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Mensagem deve ter no máximo 500 caracteres",
                    }
                ),
                400,
            )

        # Sanitizar
        sanitized_message = sanitize_input(message.lower())
        user = get_user()
        logger.info(f'Usuário {user["id"]} enviou: {sanitized_message[:50]}...')

        # Gerar session_id único por sessão
        if "chat_session_id" not in session:
            session["chat_session_id"] = str(uuid.uuid4())
        # session_id = session["chat_session_id"]
        # user_id = str(user["id"]) if user and "id" in user else None

        # Classificar intent
        intent = classificar_intent(sanitized_message)
        logger.info(f"Intent detectada: {intent}")

        # Após cada resposta, salvar no histórico
        def salvar_historico(mensagem, resposta, intent):
            # save_chat_history(session_id, user_id, mensagem, resposta, intent)
            pass

        if intent == "consulta_dados":
            try:
                # query = "SELECT CATEGORIA, COUNT(*) as total_produtos FROM Admat_OPCOM GROUP BY CATEGORIA ORDER BY total_produtos DESC"
                df = get_table_df("ADMAT")
                if df is None:
                    raise Exception("Arquivo Parquet da tabela ADMAT não encontrado.")
                categorias = df["CATEGORIA"].value_counts().index.tolist()
                totais = df["CATEGORIA"].value_counts().values.tolist()
                plotly_data = {
                    "data": [
                        {
                            "x": categorias,
                            "y": totais,
                            "type": "bar",
                            "name": "Produtos",
                        }
                    ],
                    "layout": {"title": "Total de Produtos por Categoria"},
                }
                logger.info("Gráfico de produtos por categoria gerado com sucesso")
                salvar_historico(
                    message,
                    "Aqui está o gráfico de produtos por categoria:",
                    intent,
                )
                return jsonify(
                    {
                        "success": True,
                        "response": "Aqui está o gráfico de produtos por categoria:",
                        "plotly_data": plotly_data,
                        "error": None,
                    }
                )
            except Exception as e:
                logger.error(f"Erro ao gerar gráfico: {e}")
                salvar_historico(message, f"Erro ao gerar gráfico: {e}", intent)
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Erro ao gerar gráfico: {e}",
                        }
                    ),
                    500,
                )

        elif intent == "pergunta_aberta":
            resposta = consultar_openai(sanitized_message)
            salvar_historico(message, resposta, intent)
            return jsonify({"success": True, "response": resposta, "error": None})

        elif intent == "pergunta_hibrida":
            try:
                # query = "SELECT TOP 2 DATENAME(month, data_venda) as mes, SUM(valor) as total_vendas FROM vendas GROUP BY DATENAME(month, data_venda), MONTH(data_venda) ORDER BY MONTH(data_venda) DESC"
                df = get_table_df("ADMAT_SEMVENDAS")
                if df is None:
                    raise Exception(
                        "Arquivo Parquet da tabela ADMAT_SEMVENDAS não encontrado."
                    )
                # Exemplo: simular meses e valores
                meses = ["Janeiro", "Fevereiro"]
                valores = [10000, 8000]
                explicacao = "Janeiro teve vendas maiores que Fevereiro devido à promoção de início de ano."
                plotly_data = {
                    "data": [
                        {
                            "x": meses[::-1],
                            "y": valores[::-1],
                            "type": "bar",
                            "name": "Vendas",
                        }
                    ],
                    "layout": {"title": "Comparativo de Vendas"},
                }
                salvar_historico(message, explicacao, intent)
                return jsonify(
                    {
                        "success": True,
                        "response": explicacao,
                        "plotly_data": plotly_data,
                        "error": None,
                    }
                )
            except Exception as e:
                logger.error(f"Erro ao gerar resposta híbrida: {e}")
                salvar_historico(
                    message, f"Erro ao gerar resposta híbrida: {e}", intent
                )
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Erro ao gerar resposta híbrida: {e}",
                        }
                    ),
                    500,
                )

        elif intent == "arquivo":
            # Bloco de análise de arquivo com pandas removido/comentado
            # if "uploaded_file_df" not in session:
            #     salvar_historico(
            #         message, "Nenhum arquivo enviado ou sessão expirada.", intent
            #     )
            #     return jsonify(
            #         {
            #             "success": False,
            #             "error": "Nenhum arquivo enviado ou sessão expirada.",
            #         }
            #     )
            # try:
            #     df = pd.read_json(session["uploaded_file_df"], orient="split")
            #     # Perguntas simples: média, soma, contagem de colunas
            #     if "média" in sanitized_message or "media" in sanitized_message:
            #         for col in df.select_dtypes(include="number").columns:
            #             if col.lower() in sanitized_message:
            #                 media = df[col].mean()
            #                 resposta = f"A média da coluna {col} é {media:.2f}"
            #                 salvar_historico(message, resposta, intent)
            #                 return jsonify(
            #                     {"success": True, "response": resposta, "error": None}
            #                 )
            #         salvar_historico(
            #             message, "Coluna não encontrada para média.", intent
            #         )
            #         return jsonify(
            #             {"success": False, "error": "Coluna não encontrada para média."}
            #         )
            #     if "soma" in sanitized_message:
            #         for col in df.select_dtypes(include="number").columns:
            #             if col.lower() in sanitized_message:
            #                 soma = df[col].sum()
            #                 resposta = f"A soma da coluna {col} é {soma:.2f}"
            #                 salvar_historico(message, resposta, intent)
            #                 return jsonify(
            #                     {"success": True, "response": resposta, "error": None}
            #                 )
            #         salvar_historico(
            #             message, "Coluna não encontrada para soma.", intent
            #         )
            #         return jsonify(
            #             {"success": False, "error": "Coluna não encontrada para soma."}
            #         )
            #     if "coluna" in sanitized_message:
            #         resposta = f"O arquivo possui as colunas: {', '.join(df.columns)}"
            #         salvar_historico(message, resposta, intent)
            #         return jsonify(
            #             {"success": True, "response": resposta, "error": None}
            #         )
            #     if "quantidade" in sanitized_message or "linhas" in sanitized_message:
            #         resposta = f"O arquivo possui {df.shape[0]} linhas e {df.shape[1]} colunas."
            #         salvar_historico(message, resposta, intent)
            #         return jsonify(
            #             {"success": True, "response": resposta, "error": None}
            #         )
            #     resposta = f"Arquivo carregado! Colunas: {', '.join(df.columns)}. Mostrando as 5 primeiras linhas:\n{df.head().to_string(index=False)}"
            #     salvar_historico(message, resposta, intent)
            #     return jsonify({"success": True, "response": resposta, "error": None})
            # except Exception as e:
            #     logger.error(f"Erro ao analisar arquivo: {e}")
            #     salvar_historico(message, f"Erro ao analisar arquivo: {e}", intent)
            #     return jsonify(
            #         {"success": False, "error": f"Erro ao analisar arquivo: {e}"}
            #     )
            pass

        # Resposta padrão
        response = consultar_openai(sanitized_message)
        salvar_historico(message, response, intent)
        logger.info(f"Resposta padrão enviada: {response}")
        return jsonify({"success": True, "response": response, "error": None})

    except Exception as e:
        logger.error(f"Erro na API de chat: {e}", exc_info=True)
        return (
            jsonify({"success": False, "error": f"Erro interno do servidor: {e}"}),
            500,
        )


@frontend.route("/api/chat/upload", methods=["POST"])
# @limiter.limit("10/minute")
@login_required
def chat_upload():
    """
    Faz upload de um arquivo CSV/Excel para análise pelo chatbot.
    ---
    tags:
      - Upload
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: Arquivo CSV ou Excel
    responses:
      200:
        description: Upload realizado com sucesso
        schema:
          type: object
          properties:
            success:
              type: boolean
            filename:
              type: string
            columns:
              type: array
              items:
                type: string
            shape:
              type: array
              items:
                type: integer
      400:
        description: Erro de validação ou leitura do arquivo
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    logger.info(f"Sessão atual: {dict(session)}")
    logger.info(f"Cookies recebidos: {request.cookies}")
    if "file" not in request.files:
        return (
            jsonify({"success": False, "error": "Nenhum arquivo enviado."}),
            400,
        )
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Arquivo vazio."}), 400
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return (
            jsonify({"success": False, "error": "Tipo de arquivo não suportado."}),
            400,
        )
    # Validação de tipo MIME
    file.seek(0)
    # --- Blocos dependentes de magic, pd, get_db_session, ChatHistory removidos/comentados ---
    # (Exemplo: bloco de upload de arquivo, histórico de chat com banco, etc.)
    # file.seek(0)
    # mime = magic.from_buffer(file.read(2048), mime=True)
    # file.seek(0)
    # if ext == "csv" and mime not in [
    #     "text/csv",
    #     "application/vnd.ms-excel",
    #     "text/plain",
    # ]:
    #     return jsonify({"success": False, "error": "Arquivo CSV inválido."}), 400
    # if (
    #     ext in ["xlsx", "xls"]
    #     and not mime.startswith("application/vnd.openxmlformats-officedocument")
    #     and not mime.startswith("application/vnd.ms-excel")
    # ):
    #     return jsonify({"success": False, "error": "Arquivo Excel inválido."}), 400
    # Limitar tamanho (ex: 2MB)
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > 2 * 1024 * 1024:
        return (
            jsonify({"success": False, "error": "Arquivo muito grande (máx 2MB)."}),
            400,
        )
    filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    # Ler arquivo com pandas
    try:
        if ext == "csv":
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        # Salvar resumo na sessão (apenas as 100 primeiras linhas e colunas)
        session["uploaded_file"] = filename
        session["uploaded_file_df"] = df.head(100).to_json(orient="split")
        session["uploaded_file_columns"] = df.columns.tolist()
        session["uploaded_file_shape"] = df.shape
        return jsonify(
            {
                "success": True,
                "filename": filename,
                "columns": df.columns.tolist(),
                "shape": df.shape,
            }
        )
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {e}")
        return (
            jsonify({"success": False, "error": f"Erro ao ler arquivo: {e}"}),
            400,
        )


@frontend.route("/api/chat/history", methods=["GET"])
@login_required
def api_chat_history():
    """
    Retorna o histórico de chat da sessão atual.
    ---
    tags:
      - Histórico
    responses:
      200:
        description: Lista de mensagens e respostas do chat
        schema:
          type: object
          properties:
            success:
              type: boolean
            history:
              type: array
              items:
                type: object
                properties:
                  mensagem:
                    type: string
                  resposta:
                    type: string
                  intent:
                    type: string
                  timestamp:
                    type: string
    """
    try:
        if "chat_session_id" not in session:
            return jsonify({"success": True, "history": []})
        session["chat_session_id"]
        # --- Blocos dependentes de magic, pd, get_db_session, ChatHistory removidos/comentados ---
        # (Exemplo: bloco de upload de arquivo, histórico de chat com banco, etc.)
        # db_session = get_db_session()
        # if db_session is None:
        #     return (
        #         jsonify({"success": False, "error": "Banco de dados indisponível."}),
        #         500,
        #     )
        # historico = (
        #     db_session.query(ChatHistory)
        #     .filter_by(session_id=session_id)
        #     .order_by(ChatHistory.timestamp.asc())
        #     .all()
        # )
        # history_list = [
        #     {
        #         "mensagem": h.mensagem,
        #         "resposta": h.resposta,
        #         "intent": h.intent,
        #         "timestamp": h.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        #     }
        #     for h in historico
        # ]
        # db_session.close()
        return jsonify({"success": True, "history": []})  # Placeholder for history
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}")
        return jsonify({"success": False, "error": f"Erro ao buscar histórico: {e}"})


# ===== HANDLER DE ERROS =====
@frontend.errorhandler(404)
def not_found_error(error):
    """Handler para erro 404"""
    return render_template("404.html"), 404


@frontend.errorhandler(500)
def internal_error(error):
    """Handler para erro 500"""
    logger.error(f"Erro interno: {error}")
    return render_template("500.html"), 500


# Configurar CORS restritivo (ajuste origins conforme necessário)
CORS(
    frontend,
    resources={
        r"/api/*": {"origins": ["http://localhost:8501", "https://seu-dominio.com"]}
    },
)
