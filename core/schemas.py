# Arquivo: core/schemas.py

from pydantic import BaseModel
from typing import Optional, Any

# --- Esquemas de Autenticação ---

class Token(BaseModel):
    """Modelo para o token de acesso retornado ao cliente."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Modelo para os dados contidos dentro do JWT."""
    username: Optional[str] = None
    role: Optional[str] = None

class User(BaseModel):
    """Modelo base para um usuário."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    role: str

class UserInDB(User):
    """Modelo para o usuário como armazenado no banco, incluindo a senha com hash."""
    hashed_password: str


# --- Esquemas da API de Consulta ---

class QueryRequest(BaseModel):
    """Modelo para a requisição de uma nova consulta do usuário."""
    text: str
    session_id: Optional[str] = None # Para manter o histórico da conversa

class QueryResponse(BaseModel):
    """Modelo para a resposta da consulta do agente."""
    response_type: str  # Ex: 'text', 'table', 'chart'
    data: Any             # O conteúdo da resposta (string, JSON para tabela/gráfico)
    session_id: str
