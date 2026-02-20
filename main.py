# API de Livros

# GET - Buscar os dados dos livros
# POST - Adicionar novos livros
# Querry String = http://127.0.0.1:8000/adiciona?id_livro=1&titulo_livro=Carlos&autor_livro=Alan&ano_livro=2002
# PUT - Atualizar informações dos livros
# DELETE - Deletar informações dos livros

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets

import os

# SQLAlchemy imports para configuração do banco de dados
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(
    title="API de Livros",
    description="API para gerenciar catálogo de livros",
    version="1.0.0",
    contact={"name": "Alan Vila Nova", "email": "alanjvpn@gmail.com"},
)

MEU_USUARIO = os.getenv("MEU_USUARIO")
MINHA_SENHA = os.getenv("MINHA_SENHA")

security = HTTPBasic()

meus_livros = {}


class Livro(BaseModel):
    titulo_livro: str
    autor_livro: str
    ano_livro: int


# Modelo SQLAlchemy para a tabela de livros
class LivroDB(Base):
    __tablename__ = "livros"

    id_livro = Column(Integer, primary_key=True, index=True)
    titulo_livro = Column(String, index=True)
    autor_livro = Column(String, index=True)
    ano_livro = Column(Integer)


# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)


# Dependência para obter a sessão do banco de dados
def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Função para autenticar o usuário usando HTTP Basic Authentication
def autenticar_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, MEU_USUARIO)
    correct_password = secrets.compare_digest(credentials.password, MINHA_SENHA)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )


# GET - Buscar os dados dos livros
@app.get("/livros")
def get_livros(
    page: int = 1,
    limit: int = 10,    
    db: SessionLocal = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario),
):
    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Valores de página e limite devem ser maiores que zero.",
        )

    livros_db = db.query(LivroDB).offset((page - 1) * limit).limit(limit).all()
    total_livros = db.query(LivroDB).count()

    if not livros_db:
        return {"message": "Não existe nenhum livro."}
    else:
        return {
            "page": page,
            "limit": limit,
            "total": total_livros,
            "livros": [
                {
                    "id_livro": livro.id_livro,
                    "titulo_livro": livro.titulo_livro,
                    "autor_livro": livro.autor_livro,
                    "ano_livro": livro.ano_livro,
                }
                for livro in livros_db
            ],
        }


# POST - Adicionar novos livros
@app.post("/adiciona")
def post_livros(
    livro: Livro,
    db: SessionLocal = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario),
):
    livro_db = (
        db.query(LivroDB)
        .filter(
            LivroDB.titulo_livro == livro.titulo_livro,
            LivroDB.autor_livro == livro.autor_livro,
        )
        .first()
    )
    if livro_db:
        raise HTTPException(status_code=400, detail="Esse Livro já existe no catálogo.")

    novo_livro = LivroDB(
        titulo_livro=livro.titulo_livro,
        autor_livro=livro.autor_livro,
        ano_livro=livro.ano_livro,
    )
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)

    return {"message": f"O livro {novo_livro.titulo_livro} foi adicionado com sucesso!"}


# PUT - Atualizar informações dos livros
@app.put("/atualiza/{id_livro}")
def put_livros(
    id_livro: int,
    livro: Livro,
    db: SessionLocal = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario),
):
    livro_db = db.query(LivroDB).filter(LivroDB.id_livro == id_livro).first()
    if not livro_db:
        raise HTTPException(
            status_code=404, detail="Esse Livro não foi encontrado no catálogo."
        )

    livro_db.titulo_livro = livro.titulo_livro
    livro_db.autor_livro = livro.autor_livro
    livro_db.ano_livro = livro.ano_livro

    db.commit()
    db.refresh(livro_db)

    return {"message": f"O livro {livro_db.titulo_livro} foi atualizado com sucesso!"}


# DELETE - Deletar informações dos livros
@app.delete("/deletar/{id_livro}")
def delete_livro(
    id_livro: int,
    db: SessionLocal = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario),
):
    livro_db = db.query(LivroDB).filter(LivroDB.id_livro == id_livro).first()
    if not livro_db:
        raise HTTPException(
            status_code=404, detail="Esse Livro não foi encontrado para ser deletado"
        )
    else:
        db.delete(livro_db)
        db.commit()
        return {"message": f"O livro {livro_db.titulo_livro} foi deletado com sucesso!"}
