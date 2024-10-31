from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import time
import asyncpg
import os

# Conexão com o banco de dados PostgreSQL
async def get_database():
    DATABASE_URL = os.environ.get("PGURL", "postgres://postgres:postgres@db:5432/filmes") 
    return await asyncpg.connect(DATABASE_URL)

# Inicializar a aplicação FastAPI
app = FastAPI()

# Modelo para adicionar novos filmes
class Filme(BaseModel):
    id: Optional[int] = None
    titulo: str
    diretor: str
    quantidade: int
    preco: float

class FilmeBase(BaseModel):
    titulo: str
    diretor: str
    quantidade: int
    preco: float

# Modelo para venda de filmes
class VendaFilme(BaseModel):
    quantidade: int

# Modelo para atualizar atributos de um filme (exceto o ID)
class AtualizarFilme(BaseModel):
    titulo: Optional[str] = None
    diretor: Optional[str] = None
    quantidade: Optional[int] = None
    preco: Optional[float] = None

# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path}, Method: {request.method}, Process Time: {process_time:.4f}s")
    return response

# Função para verificar se o filme existe usando diretor e nome do filme
async def filme_existe(titulo: str, diretor: str, conn: asyncpg.Connection):
    try:
        query = "SELECT * FROM filmes WHERE LOWER(titulo) = LOWER($1) AND LOWER(diretor) = LOWER($2)"
        result = await conn.fetchval(query, titulo, diretor)
        return result is not None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao verificar se o filme existe: {str(e)}")

# 1. Adicionar um novo filme
@app.post("/api/v1/filmes/", status_code=201)
async def adicionar_filme(filme: FilmeBase):
    conn = await get_database()
    if await filme_existe(filme.titulo, filme.diretor, conn):
        raise HTTPException(status_code=400, detail="Filme já existe.")
    try:
        query = "INSERT INTO filmes (titulo, diretor, quantidade, preco) VALUES ($1, $2, $3, $4)"
        async with conn.transaction():
            result = await conn.execute(query, filme.titulo, filme.diretor, filme.quantidade, filme.preco)
            return {"message": "Filme adicionado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao adicionar o filme: {str(e)}")
    finally:
        await conn.close()

# 2. Listar todos os filmes
@app.get("/api/v1/filmes/", response_model=List[Filme])
async def listar_filmes():
    conn = await get_database()
    try:
        # Buscar todos os filmes no banco de dados
        query = "SELECT * FROM filmes"
        rows = await conn.fetch(query)
        filmes = [dict(row) for row in rows]
        return filmes
    finally:
        await conn.close()

# 3. Buscar filme por ID
@app.get("/api/v1/filmes/{filme_id}")
async def listar_filme_por_id(filme_id: int):
    conn = await get_database()
    try:
        # Buscar o filme por ID
        query = "SELECT * FROM filme WHERE id = $1"
        filme = await conn.fetchrow(query, filme_id)
        if filme is None:
            raise HTTPException(status_code=404, detail="Filme não encontrado.")
        return dict(filme)
    finally:
        await conn.close()

# 4. Vender um filme (reduzir quantidade no estoque)
@app.put("/api/v1/filmes/{filmes_id}/vender/")
async def vender_filme(filme_id: int, venda: VendaFilme):
    conn = await get_database()
    try:
        # Verificar se o filme existe
        query = "SELECT * FROM filmes WHERE id = $1"
        filme = await conn.fetchrow(query, filme_id)
        if filme is None:
            raise HTTPException(status_code=404, detail="Filme não encontrado.")

        # Verificar se a quantidade no estoque é suficiente
        if filme['quantidade'] < venda.quantidade:
            raise HTTPException(status_code=400, detail="Quantidade insuficiente no estoque.")

        # Atualizar a quantidade no banco de dados
        nova_quantidade = filme['quantidade'] - venda.quantidade
        update_query = "UPDATE livros SET quantidade = $1 WHERE id = $2"
        await conn.execute(update_query, nova_quantidade, filme_id)


        # Calcular o valor total da venda
        valor_venda = filme['preco'] * venda.quantidade
        # Registrar a venda na tabela de vendas
        insert_venda_query = """
            INSERT INTO vendas (filme_id, quantidade_vendida, valor_venda) 
            VALUES ($1, $2, $3)
        """
        await conn.execute(insert_venda_query, filme_id, venda.quantidade, valor_venda)

        # Criar um novo dicionário com os dados atualizados
        filme_atualizado = dict(filme)
        filme_atualizado['quantidade'] = nova_quantidade

        return {"message": "Venda realizada com sucesso!", "filme": filme_atualizado}
    finally:
        await conn.close()

# 5. Atualizar atributos de um filme pelo ID (exceto o ID)
@app.patch("/api/v1/filmes/{filme_id}")
async def atualizar_filme(filme_id: int, filme_atualizacao: AtualizarFilme):
    conn = await get_database()
    try:
        # Verificar se o livro existe
        query = "SELECT * FROM filmes WHERE id = $1"
        livro = await conn.fetchrow(query, filme_id)
        if livro is None:
            raise HTTPException(status_code=404, detail="Filme não encontrado.")

        # Atualizar apenas os campos fornecidos
        update_query = """
            UPDATE filmes
            SET titulo = COALESCE($1, titulo),
                diretor = COALESCE($2, diretor),
                quantidade = COALESCE($3, quantidade),
                preco = COALESCE($4, preco)
            WHERE id = $5
        """
        await conn.execute(
            update_query,
            filme_atualizacao.titulo,
            filme_atualizacao.diretor,
            filme_atualizacao.quantidade,
            filme_atualizacao.preco,
            filme_id
        )
        return {"message": "Filme atualizado com sucesso!"}
    finally:
        await conn.close()

# 6. Remover um filme pelo ID
@app.delete("/api/v1/filmes/{filme_id}")
async def remover_filme(filme_id: int):
    conn = await get_database()
    try:
        # Verificar se o filme existe
        query = "SELECT * FROM filmes WHERE id = $1"
        filme = await conn.fetchrow(query, filme_id)
        if filme is None:
            raise HTTPException(status_code=404, detail="Filme não encontrado.")

        # Remover o filme do banco de dados
        delete_query = "DELETE FROM filmes WHERE id = $1"
        await conn.execute(delete_query, filme_id)
        return {"message": "Filme removido com sucesso!"}
    finally:
        await conn.close()

# 7. Resetar repositorio de filmes
@app.delete("/api/v1/filmes/")
async def resetar_filmes():
    init_sql = os.getenv("INIT_SQL", "db/init.sql")
    conn = await get_database()
    try:
        # Read SQL file contents
        with open(init_sql, 'r') as file:
            sql_commands = file.read()
        # Execute SQL commands
        await conn.execute(sql_commands)
        return {"message": "Banco de dados limpo com sucesso!!"}
    finally:
        await conn.close()


# 8 . Listar vendas
@app.get("/api/v1/vendas/")
async def listar_vendas():
    conn = await get_database()
    try:
        # Buscar todas as vendas no banco de dados
        query = "SELECT * FROM vendas"
        rows = await conn.fetch(query)
        vendas = [dict(row) for row in rows]
        return vendas
    finally:
        await conn.close()