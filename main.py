# API de Livros

# GET - Buscar os dados dos livros
# POST - Adicionar novos livros
# Querry String = http://127.0.0.1:8000/adiciona?id_livro=1&titulo_livro=Carlos&autor_livro=Alan&ano_livro=2002
# PUT - Atualizar informações dos livros
# DELETE - Deletar informações dos livros

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets
import os
import redis
import json
from tasks import somar, fatorial
from celery_app import celery_app
from celery.result import AsyncResult

# SQLAlchemy imports para configuração do banco de dados
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

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

def salvar_livros_redis(livro_id: int, livro_db: LivroDB):
    livro_dict = {
        "id_livro": livro_id,
        "titulo_livro": livro_db.titulo_livro,
        "autor_livro": livro_db.autor_livro,
        "ano_livro": livro_db.ano_livro
    }
    redis_client.set(f"livro:{livro_id}", json.dumps(livro_dict))

def deletar_livros_redis(livro_id: int):
    redis_client.delete(f"livro:{livro_id}")

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

@app.get("/")
def hello():
    return {"message": "Bem-vindo à API de Livros!"}

@app.post("/calcular/soma")
def calcular_soma(num1: int, num2: int):
    tarefa = somar.delay(num1, num2)
    return {"task_id": tarefa.id, "message": "Tarefa de soma iniciada"}

@app.post("/calcular/fatorial")
def calcular_fatorial(num: int):
    tarefa = fatorial.delay(num)
    return {"task_id": tarefa.id, "message": "Tarefa de fatorial iniciada"}

@app.get("/debug/redis")
def ver_livros_redis():
    chaves = redis_client.keys("livro:*")
    livros_redis = []

    for chave in chaves:
        valor = redis_client.get(chave)
        ttl = redis_client.ttl(chave)
        
        if valor:
            livros_redis.append({"chave": chave, "valor": json.loads(valor), "ttl": ttl})

    return livros_redis

# GET - Buscar os dados dos livros
@app.get("/livros")
async def get_livros(
    page: int = 1,
    limit: int = 10,    
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario),
):
    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Valores de página e limite devem ser maiores que zero.",
        )

    cache_key = f"livros_page_{page}_limit_{limit}"
    cache_result = redis_client.get(cache_key)

    if cache_result:
        return json.loads(cache_result)
    

    livros_db = db.query(LivroDB).offset((page - 1) * limit).limit(limit).all()
    
    if not livros_db:
        return {"message": "Não existe nenhum livro."}
    
    total_livros = db.query(LivroDB).count()

    
    resultado = {
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
    
    redis_client.setex(cache_key, 30, json.dumps(resultado))  # Cache por 30 segundos
    return resultado


    
# POST - Adicionar novos livros
@app.post("/adiciona")
async def post_livros(
    livro: Livro,
    db: Session = Depends(sessao_db),
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
    salvar_livros_redis(novo_livro.id_livro, novo_livro)

    return {"message": f"O livro {novo_livro.titulo_livro} foi adicionado com sucesso!"}


# PUT - Atualizar informações dos livros
@app.put("/atualiza/{id_livro}")
async def put_livros(
    id_livro: int,
    livro: Livro,
    db: Session = Depends(sessao_db),
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

    salvar_livros_redis(id_livro, livro_db)

    return {"message": f"O livro {livro_db.titulo_livro} foi atualizado com sucesso!"}


# DELETE - Deletar informações dos livros
@app.delete("/deletar/{id_livro}")
async def delete_livro(
    id_livro: int,
    db: Session = Depends(sessao_db),
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
        deletar_livros_redis(id_livro)
        return {"message": f"O livro {livro_db.titulo_livro} foi deletado com sucesso!"}
