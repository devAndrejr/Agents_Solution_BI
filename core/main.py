# core/main.py
import uvicorn
import logging
import subprocess
import sys
from datetime import timedelta

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Módulos locais
from core import schemas, security
from core.database import sql_server_auth_db as auth_db
from core.query_processor import QueryProcessor
from core.config.logging_config import setup_logging

# --- Configuração Inicial ---
setup_logging()

app = FastAPI(
    title="Agent_BI Backend",
    description="Serviço de backend para o Agente de BI, incluindo API de consulta e agendamento de tarefas.",
    version="2.0.0"
)

scheduler = AsyncIOScheduler()

# --- Lógica do Pipeline de Dados (Existente) ---
def get_db_credentials_from_file() -> dict:
    creds = {}
    try:
        with open("conexao.txt", "r") as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    creds[key.strip().lower()] = value.strip().strip("'")
    except FileNotFoundError:
        logging.warning("Arquivo conexao.txt não encontrado.")
    return creds

def trigger_pipeline_subprocess():
    logging.info("Acionando a execução do pipeline de dados via subprocesso...")
    creds = get_db_credentials_from_file()
    if not all(k in creds for k in ['server', 'database', 'user', 'password']):
        logging.error("Credenciais insuficientes para executar o pipeline.")
        return
    command = [sys.executable, "scripts/data_pipeline.py", "--server", creds['server'], "--database", creds['database'], "--user", creds['user'], "--password", creds['password']]
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        logging.info(f"Subprocesso do pipeline executado com sucesso: {process.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Subprocesso do pipeline falhou: {e.stderr}")

# --- Lógica de Autenticação e Dependências da API ---
def get_current_active_user(current_user: schemas.User = Depends(security.get_current_user)) -> schemas.User:
    # No futuro, esta função pode verificar se o usuário está desabilitado no banco de dados.
    # Por enquanto, a verificação está implícita no token.
    return current_user

# --- Endpoints da API ---
api_router = APIRouter(prefix="/api/v1")

@api_router.post("/auth/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    role, error_msg = auth_db.autenticar_usuario(form_data.username, form_data.password)
    if not role:
        logging.warning(f"Tentativa de login falha para o usuário {form_data.username}: {error_msg or 'Credenciais incorretas'}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_msg or "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": form_data.username, "role": role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/queries/", response_model=schemas.QueryResponse, tags=["Queries"])
async def handle_query(
    query: schemas.QueryRequest,
    current_user: schemas.User = Depends(get_current_active_user)
):
    try:
        # A inicialização do QueryProcessor pode precisar de mais contexto
        query_processor = QueryProcessor(user_id=current_user.username)
        # O método a ser chamado pode variar
        agent_response = await query_processor.process(query.text, query.session_id)
        return schemas.QueryResponse(**agent_response)
    except Exception as e:
        logging.error(f"Erro ao processar a consulta para o usuário {current_user.username}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a sua pergunta.")

@api_router.get("/users/me", response_model=schemas.User, tags=["Users"])
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

# --- Endpoints de Monitoramento e Ações (Existentes) ---
@app.get("/status", tags=["Monitoring"])
def read_root():
    return {"status": "Serviço de Backend do Agent_BI está no ar."}

@app.post("/run-pipeline", tags=["Actions"])
async def trigger_pipeline_endpoint():
    logging.info("Execução manual do pipeline de dados acionada via API.")
    scheduler.add_job(trigger_pipeline_subprocess, 'date', name="Execução Manual do Pipeline")
    return {"message": "Execução do pipeline de dados iniciada."}

# --- Inicialização ---
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    logging.info("Iniciando o agendador de tarefas do backend...")
    scheduler.add_job(
        trigger_pipeline_subprocess,
        trigger=CronTrigger(hour='8,20', minute='0'),
        id="data_pipeline_job",
        name="Pipeline de Extração de Dados SQL para Parquet",
        replace_existing=True
    )
    scheduler.start()
    logging.info("Agendador iniciado.")

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Encerrando o agendador de tarefas...")
    scheduler.shutdown()