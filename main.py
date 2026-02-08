# API de Livros

# GET - Buscar os dados dos livros
# POST - Adicionar novos livros
# Querry String = http://127.0.0.1:8000/adiciona?id_livro=1&titulo_livro=Carlos&autor_livro=Alan&ano_livro=2002
# PUT - Atualizar informações dos livros
# DELETE - Deletar informações dos livros

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

meus_livros = {}

class Livro(BaseModel):
    titulo_livro: str
    autor_livro: str
    ano_livro: int

@app.get("/livros")
def get_livros():
    if not meus_livros:
        return {"message:" "Não existe nenhum livro."}
    else:
        return {"livros": meus_livros}


# ID, nome, autor, ano
@app.post("/adiciona")
def post_livros(id_livro: int, livro: Livro):
    if id_livro in meus_livros:
        raise HTTPException(status_code=400, detail="Esse Livro já existe")
    else:
        meus_livros[id_livro] = livro.dict()
        return {"message": "O livro foi adicionado com sucesso!"}


@app.put("/atualiza/{id_livro}")
def put_livros(id_livro: int,livro: Livro):
    meu_livro = meus_livros.get(id_livro)
    if not meu_livro:
        raise HTTPException(status_code=404, detail="Esse Livro não foi encontrado")
    else:
        meus_livros[id_livro] = livro.dict()
        
        return {"message": "As informações do Livro foram atualizadas!"}


@app.delete("/deletar/{id_livro}")
def delete_livro(id_livro: int):
    if id_livro not in meus_livros:
        raise HTTPException(status_code=404, detail="Esse Livro não foi encontrado")
    else:
        del meus_livros[id_livro]
        
        return {"message": "Seu livro foi deletado!"}     
