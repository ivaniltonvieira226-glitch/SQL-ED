from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
from lib import (
    mostrar_livros,
    buscar_por_id,
    buscar_livro,
    filtrar_ano,
    ordenar_cresc,
    ordenar_desc,
    remover_livro,
    atualizar_leitura,
    inserir_livro
)

app = FastAPI()

#PERMISSÃO CORS: Libera para que o seu Front-end em JavaScript consiga conversar com esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite requisições de qualquer origem (perfeito para uso local)
    allow_credentials=True,
    allow_methods=["*"],  # Libera GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

# Modelo para criação de novos livros (POST)
class Livro(BaseModel):
    titulo: str 
    pagina: int
    ano: int
    autor: str
    status: str
    pagina_atual: int

# Modelo para atualização de leitura (PUT)
class AtualizacaoLeitura(BaseModel):
    status: str
    pagina_atual: int


# ==============================================================================
# MÉTODOS DE BUSCA (GET)
# ==============================================================================

@app.get("/livros")
def listar_todos_livros():
    return mostrar_livros()


@app.get("/livros/id/{id}")
def consultar_id(id: int):
    livro = buscar_por_id(id)
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro


@app.get("/livros/titulo/{titulo}")
def consultar_livro(titulo: str):
    return buscar_livro(titulo)


@app.get("/livros/ano/{ano}")
def filtrar_ano_livro(ano: int):
    return filtrar_ano(ano)


@app.get("/livros/ordenar/cresc")
def ano_cresc():
    return ordenar_cresc()


@app.get("/livros/ordenar/desc")
def ano_desc():
    return ordenar_desc()


# ==============================================================================
# MÉTODO DE REMOÇÃO (DELETE)
# ==============================================================================

@app.delete("/livros/{id}")
def remover(id: int):
    try:
        remover_livro(id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"mensagem": "Livro removido com sucesso"}


# ==============================================================================
# MÉTODO DE ATUALIZAÇÃO (PUT)
# ==============================================================================

@app.put("/livros/{livro_id}")
def update(livro_id: int, dados: AtualizacaoLeitura): # <-- Agora os dados vêm encapsulados do JS!
    try:
        atualizar_leitura(livro_id, dados.status, dados.pagina_atual)
    except ValueError as e:
        # Se na lib a validação falhar (ex: página atual > total), a API avisa o front de forma limpa
        raise HTTPException(status_code=400, detail=str(e))
    return {"mensagem": "Leitura atualizada com sucesso"}


# ==============================================================================
# MÉTODO DE CRIAÇÃO (POST)
# ==============================================================================

@app.post("/livros")
def novo_livro(livro: Livro):
    try:
        inserir_livro(
            livro.titulo, livro.pagina, livro.ano,
            livro.autor, livro.status, livro.pagina_atual
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return {"mensagem": "Livro adicionado com sucesso"}