from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import time

# Banco de dados simulado (em memória)
estoque = [
    {"id": 1, "nome": "Produto A", "descricao": "Descricao A", "quantidade": 10, "preco": 30.0},
    {"id": 2, "nome": "Produto B", "descricao": "Descricao B", "quantidade": 5, "preco": 13.0},
]

app = FastAPI()

# Modelo de item no estoque
class Item(BaseModel):
    id: int
    nome: str
    descricao: str = None
    preco: float
    quantidade: int

# Função para gerar o próximo ID dinamicamente
def gerar_proximo_id():
    if estoque:
        return max(item['id'] for item in estoque) + 1
    else:
        return 1
    
# Função auxiliar para buscar itens por ID
def buscar_itens_por_id(item_id: int):
    for item in estoque:
        if item["id"] == item_id:
            return item
    return None

# Função para venda de itens
class VendaItem(BaseModel):
    quantidade: int

# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path}, Method: {request.method}, Process Time: {process_time:.4f}s")
    return response
    
    
# Rota para criar um novo item
@app.post("/api/v1/estoque/", status_code=201)
# Adicionar novo item
def adicionar_item(item: Item):
    # Verificando se o item já existe
    for i in estoque:
        if i["nome"].lower() == item.nome.lower():
            raise HTTPException(status_code=400, detail="Item já existe")
    
    # Gerando ID dinamicamente
    novo_item = item.dict()
    novo_item['id'] = gerar_proximo_id()

    # Adicionando item ao repositório
    estoque.append(novo_item)
    return {"message": "Item adicionado com sucesso!"}


# Rota para listar todos os itens
@app.get("/api/v1/estoque/", response_model=List[Item])
# Listar itens
def listar_itens():
    return estoque


# Rota para consultar um item pelo ID
@app.get("/api/v1/estoque/{item_id}")
# Listar itens pelo ID
def listar_itens_por_id(item_id: int):
    # Buscando por ID com função auxiliar
    item = buscar_itens_por_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item


# Atualizar atributos de um item (exceto o ID)
class AtualizarItem(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    quantidade: Optional[int] = None
    preco: Optional[float] = None
    
# Rota para atualizar um item
@app.patch("/api/v1/estoque/{item_id}")
# Atualizar item
def atualizar_item(item_id: int, item_atualizacao: AtualizarItem):
    # Buscando por ID com função auxiliar
    item = buscar_itens_por_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    # Atualizando apenas os campos fornecidos
    if item_atualizacao.nome is not None:
        item["nome"] = item_atualizacao.nome
    if item_atualizacao.descricao is not None:
        item["descricao"] = item_atualizacao.descricao
    if item_atualizacao.quantidade is not None:
        item["quantidade"] = item_atualizacao.quantidade
    if item_atualizacao.preco is not None:
        item["preco"] = item_atualizacao.preco

    return {"message": "Item atualizado com sucesso!", "item": item}


# Rota para deletar um item
@app.delete("/api/v1/estoque/{item_id}")
# Deletar item
def remover_item(item_id: int):
    for i, item in enumerate(estoque):
        if item["id"] == item_id:
            del estoque[i]
            return {"message": "Item removido com sucesso!"}
        

# Rota para vender um item (reduzir quantidade no estoque)
@app.put("/api/v1/estoque/{item_id}/vender/")
# Deletar item
def vender_item(item_id: int, venda: VendaItem):
    item = buscar_itens_por_id(item_id)
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    if item["quantidade"] < venda.quantidade:
        raise HTTPException(status_code=400, detail="Quantidade indisponível")
    
    item["quantidade"] -= venda.quantidade
    return {"message": "Venda realizada com sucesso!", "item": item}

# Rota para resetar repositorio
@app.delete("/api/v1/estoque/")
# Deletar todos os itens
def resetar_itens():
    global estoque
    estoque = [
    {"id": 1, "nome": "Produto A", "descricao": "Descricao A", "quantidade": 10, "preco": 30.0},
    {"id": 2, "nome": "Produto B", "descricao": "Descricao B", "quantidade": 5, "preco": 13.0},
]
    return {"message": "Repositorio limpo com sucesso!", "itens": estoque}