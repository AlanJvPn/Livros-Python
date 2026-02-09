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

app = FastAPI(
    title="API de Livros",
    description="API para gerenciar catálogo de livros",
    version="1.0.0",
    contact={
        "name": "Alan Vila Nova",
        "email": "alanjvpn@gmail.com"
    }
    )

MEU_USUARIO = "admin"
MINHA_SENHA = "admin"

security = HTTPBasic()

meus_livros = {}

class Livro(BaseModel):
    titulo_livro: str
    autor_livro: str
    ano_livro: int

def autenticar_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, MEU_USUARIO)
    correct_password = secrets.compare_digest(credentials.password, MINHA_SENHA)
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas", headers={"WWW-Authenticate": "Basic"})


@app.get("/livros")
def get_livros(page: int = 1, limit: int = 10, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Valores de página e limite devem ser maiores que zero.")

    if not meus_livros:
        return {"message": "Não existe nenhum livro."}
    else:

        livros_ordenados = sorted(meus_livros.items(), key=lambda x: int(x[0]))
        start = (page - 1) * limit
        end = start + limit

        ##livros_paginados = [{"id": id_livro, **livro} for id_livro, livro in list(meus_livros.items())[start:end]]
        livros_paginados = [{"id": id_livro, "titulo_livro": livro_data["titulo_livro"], "autor_livro": livro_data["autor_livro"], "ano_livro": livro_data["ano_livro"]} 
                            for id_livro, livro_data in livros_ordenados[start:end]]
        
        return {"page": page, "limit": limit, "total": len(meus_livros), "livros": livros_paginados}


# ID, nome, autor, ano
@app.post("/adiciona")
def post_livros(id_livro: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if id_livro in meus_livros:
        raise HTTPException(status_code=400, detail="Esse Livro já existe")
    else:
        meus_livros[id_livro] = livro.dict()
        return {"message": "O livro foi adicionado com sucesso!"}


@app.put("/atualiza/{id_livro}")
def put_livros(id_livro: int,livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    meu_livro = meus_livros.get(id_livro)
    if not meu_livro:
        raise HTTPException(status_code=404, detail="Esse Livro não foi encontrado")
    else:
        meus_livros[id_livro] = livro.dict()
        
        return {"message": "As informações do Livro foram atualizadas!"}


@app.delete("/deletar/{id_livro}")
def delete_livro(id_livro: int, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if id_livro not in meus_livros:
        raise HTTPException(status_code=404, detail="Esse Livro não foi encontrado")
    else:
        del meus_livros[id_livro]
        
        return {"message": "Seu livro foi deletado!"}     
