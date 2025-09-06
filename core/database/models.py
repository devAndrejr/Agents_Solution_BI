from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    ativo = Column(Boolean, default=True)
    tentativas_invalidas = Column(Integer, default=0)
    bloqueado_ate = Column(DateTime, nullable=True)
    ultimo_login = Column(DateTime, nullable=True)
    redefinir_solicitado = Column(Boolean, default=False)
    redefinir_aprovado = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"
