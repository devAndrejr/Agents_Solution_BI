import pyodbc
from datetime import datetime, timedelta
from sqlalchemy import text
import logging

from core.utils.db_connection import get_db_connection
from core.utils.security_utils import get_password_hash, verify_password # Importar de core.security

# --- Constantes de Autenticação ---
MAX_TENTATIVAS = 5
BLOQUEIO_MINUTOS = 15
SESSAO_MINUTOS = 30

logger = logging.getLogger(__name__)

# --- Inicialização do banco (Cria a tabela se não existir) ---
def init_db():
    logger.info("Iniciando a inicialização do banco de dados de autenticação.")
    with get_db_connection() as conn:
        conn.execute(
            text(
                """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='usuarios' and xtype='U')
                CREATE TABLE usuarios (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    username NVARCHAR(255) UNIQUE NOT NULL,
                    password_hash NVARCHAR(255) NOT NULL,
                    role NVARCHAR(50) NOT NULL,
                    ativo BIT DEFAULT 1,
                    tentativas_invalidas INT DEFAULT 0,
                    bloqueado_ate DATETIME,
                    ultimo_login DATETIME,
                    redefinir_solicitado BIT DEFAULT 0,
                    redefinir_aprovado BIT DEFAULT 0
                );
                """
            )
        )
        conn.commit()
    logger.info("Banco de dados de autenticação inicializado com sucesso.")

# --- Criação de usuário ---
def criar_usuario(username, password, role="user"):
    logger.info(f"Tentando criar usuário: {username} com perfil: {role}")
    password_hash = get_password_hash(password)
    try:
        with get_db_connection() as conn:
            conn.execute(
                text("INSERT INTO usuarios (username, password_hash, role) VALUES (:username, :password_hash, :role)"),
                {"username": username, "password_hash": password_hash, "role": role},
            )
            conn.commit()
        logger.info(f"Usuário '{username}' criado com sucesso.")
    except pyodbc.IntegrityError:
        logger.warning(f"Tentativa de criar usuário existente: {username}")
        raise ValueError("Usuário já existe")
    except Exception as e:
        logger.error(f"Erro ao criar usuário {username}: {e}", exc_info=True)
        raise

# --- Autenticação ---
def autenticar_usuario(username, password):
    logger.info(f"Tentativa de autenticação para o usuário: {username}")
    try:
        with get_db_connection() as conn:
            result = conn.execute(
                text("SELECT id, password_hash, ativo, tentativas_invalidas, bloqueado_ate, role FROM usuarios WHERE username=:username"),
                {"username": username}
            ).fetchone()

            if not result:
                logger.warning(f"Usuário '{username}' não encontrado no banco de dados.")
                return None, "Usuário não encontrado"
            
            user_id, db_password_hash, ativo, tentativas, bloqueado_ate, role = result
            now = datetime.now()

            logger.info(f"Usuário '{username}' encontrado. Ativo: {ativo}, Tentativas: {tentativas}, Bloqueado até: {bloqueado_ate}")

            if not ativo:
                logger.warning(f"Usuário '{username}' inativo ou bloqueado.")
                return None, "Usuário inativo ou bloqueado"

            if bloqueado_ate and now < bloqueado_ate:
                logger.warning(f"Usuário '{username}' bloqueado até {bloqueado_ate.strftime('%Y-%m-%d %H:%M:%S')}.")
                return None, f"Usuário bloqueado até {bloqueado_ate.strftime('%Y-%m-%d %H:%M:%S')}"

            logger.info(f"Verificando senha para o usuário: {username}")
            if not verify_password(password, db_password_hash):
                tentativas += 1
                if tentativas >= MAX_TENTATIVAS:
                    bloqueado_ate = now + timedelta(minutes=BLOQUEIO_MINUTOS)
                    conn.execute(
                        text("UPDATE usuarios SET tentativas_invalidas=:tentativas, bloqueado_ate=:bloqueado_ate WHERE id=:id"),
                        {"tentativas": tentativas, "bloqueado_ate": bloqueado_ate, "id": user_id}
                    )
                    conn.commit()
                    logger.warning(f"Usuário '{username}' bloqueado por {BLOQUEIO_MINUTOS} minutos após {tentativas} tentativas falhas.")
                    return None, f"Usuário bloqueado por {BLOQUEIO_MINUTOS} minutos"
                else:
                    conn.execute(
                        text("UPDATE usuarios SET tentativas_invalidas=:tentativas WHERE id=:id"),
                        {"tentativas": tentativas, "id": user_id}
                    )
                    conn.commit()
                    logger.warning(f"Senha incorreta para o usuário '{username}'. Tentativas restantes: {MAX_TENTATIVAS - tentativas}")
                    return (
                        None,
                        f"Senha incorreta. Tentativas restantes: {MAX_TENTATIVAS - tentativas}",
                    )
            
            # Sucesso
            conn.execute(
                text("UPDATE usuarios SET tentativas_invalidas=0, bloqueado_ate=NULL, ultimo_login=:now WHERE id=:id"),
                {"now": now, "id": user_id}
            )
            conn.commit()
            logger.info(f"Usuário '{username}' autenticado com sucesso. Papel: {role}")
            return role, None
    except Exception as e:
        logger.error(f"Erro inesperado durante a autenticação do usuário {username}: {e}", exc_info=True)
        return None, "Erro interno no servidor de autenticação."


# --- Solicitar redefinição de senha ---
def solicitar_redefinicao(username):
    logger.info(f"Solicitação de redefinição de senha para o usuário: {username}")
    try:
        with get_db_connection() as conn:
            conn.execute(
                text("UPDATE usuarios SET redefinir_solicitado=1 WHERE username=:username"),
                {"username": username}
            )
            conn.commit()
        logger.info(f"Solicitação de redefinição para '{username}' registrada.")
    except Exception as e:
        logger.error(f"Erro ao solicitar redefinição para {username}: {e}", exc_info=True)
        raise


# --- Aprovar redefinição de senha (admin) ---
def aprovar_redefinicao(username):
    logger.info(f"Aprovação de redefinição de senha para o usuário: {username}")
    try:
        with get_db_connection() as conn:
            conn.execute(
                text("UPDATE usuarios SET redefinir_aprovado=1 WHERE username=:username"),
                {"username": username}
            )
            conn.commit()
        logger.info(f"Redefinição para '{username}' aprovada.")
    except Exception as e:
        logger.error(f"Erro ao aprovar redefinição para {username}: {e}", exc_info=True)
        raise


# --- Redefinir senha (após aprovação) ---
def redefinir_senha(username, nova_senha):
    logger.info(f"Redefinindo senha para o usuário: {username}")
    try:
        with get_db_connection() as conn:
            result = conn.execute(text("SELECT redefinir_aprovado FROM usuarios WHERE username=:username"), {"username": username}).fetchone()
            if not result or not result[0]:
                logger.warning(f"Tentativa de redefinição de senha não aprovada para {username}.")
                raise ValueError("Redefinição não aprovada")
            
            password_hash = get_password_hash(nova_senha)
            conn.execute(
                text("UPDATE usuarios SET password_hash=:password_hash, redefinir_solicitado=0, redefinir_aprovado=0 WHERE username=:username"),
                {"password_hash": password_hash, "username": username},
            )
            conn.commit()
            logger.info(f"Senha de '{username}' redefinida com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao redefinir senha para {username}: {e}", exc_info=True)
        raise


# --- Expiração de sessão ---
def sessao_expirada(ultimo_login):
    if not ultimo_login:
        return True
    try:
        return (datetime.now() - ultimo_login) > timedelta(minutes=SESSAO_MINUTOS)
    except Exception as e:
        logger.error(f"Erro ao verificar expiração de sessão: {e}", exc_info=True)
        return True
