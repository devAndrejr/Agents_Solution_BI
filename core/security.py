# Arquivo: core/security.py

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from core import schemas
from core.database import sql_server_auth_db as auth_db
from core.utils.security_utils import get_password_hash, verify_password

# É CRÍTICO que esta chave seja secreta e gerenciada via variáveis de ambiente em produção.
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Define o esquema de autenticação. O tokenUrl aponta para o endpoint de login.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> schemas.User:
    """
    Decodifica o token JWT para obter o usuário atual.
    Esta função é uma dependência que pode ser usada para proteger endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception
    
    # Aqui, estamos apenas confiando nos dados do token.
    # Uma implementação mais robusta poderia verificar se o usuário ainda existe no banco de dados.
    user = schemas.User(username=token_data.username, role=token_data.role)
    if user is None:
        raise credentials_exception
    return user