from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os

app = FastAPI()

# Modelos de dados
class Quarto(BaseModel):
    id: int
    numero: str
    tipo: str
    preco: float

class Cliente(BaseModel):
    id: int
    nome: str
    cpf: int

class Reserva(BaseModel):
    id: int
    cliente_id: int
    quarto_id: int

class Item(BaseModel):
    id: int
    nome: str
    preco: float

class Compra(BaseModel):
    id: int
    cliente_id: int
    item_id: int

# Caminhos dos arquivos JSON
QUARTOS_FILE = "quartos.json"
CLIENTES_FILE = "clientes.json"
RESERVAS_FILE = "reservas.json"
ITENS_FILE = "itens.json"
COMPRAS_FILE = "compras.json"

# Funções para carregar e salvar dados
def carregar_dados(caminho: str, modelo):
    if os.path.exists(caminho):
        with open(caminho, "r") as f:
            dados = json.load(f)
            return [modelo(**item) for item in dados]
    return []

def salvar_dados(caminho: str, dados):
    with open(caminho, "w") as f:
        json.dump([d.dict() for d in dados], f, indent=4)

# Carregar dados ao iniciar
quartos: List[Quarto] = carregar_dados(QUARTOS_FILE, Quarto)
clientes: List[Cliente] = carregar_dados(CLIENTES_FILE, Cliente)
reservas: List[Reserva] = carregar_dados(RESERVAS_FILE, Reserva)
itens: List[Item] = carregar_dados(ITENS_FILE, Item)
compras: List[Compra] = carregar_dados(COMPRAS_FILE, Compra)

# Inicializar IDs
next_quarto_id = max([q.id for q in quartos], default=0) + 1
next_cliente_id = max([c.id for c in clientes], default=0) + 1
next_reserva_id = max([r.id for r in reservas], default=0) + 1
next_item_id = max([i.id for i in itens], default=0) + 1
next_compra_id = max([c.id for c in compras], default=0) + 1

# Endpoints
@app.post("/quartos/", response_model=Quarto)
async def adicionar_quarto(quarto: Quarto):
    global next_quarto_id
    quarto.id = next_quarto_id
    quartos.append(quarto)
    next_quarto_id += 1
    salvar_dados(QUARTOS_FILE, quartos)
    return quarto

@app.post("/clientes/", response_model=Cliente)
async def registrar_cliente(cliente: Cliente):
    global next_cliente_id
    cliente.id = next_cliente_id
    clientes.append(cliente)
    next_cliente_id += 1
    salvar_dados(CLIENTES_FILE, clientes)
    return cliente


@app.post("/reservas/", response_model=Reserva)
async def fazer_reserva(reserva: Reserva):
    if not any(c.id == reserva.cliente_id for c in clientes):
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if not any(q.id == reserva.quarto_id for q in quartos):
        raise HTTPException(status_code=404, detail="Quarto não encontrado")

    reservas.append(reserva)
    salvar_dados(RESERVAS_FILE, reservas)
    return reserva

@app.delete("/clientes/{cliente_id}", response_model=Cliente)
async def remover_cliente(cliente_id: int):
    for i, c in enumerate(clientes):
        if c.id == cliente_id:
            cliente = clientes.pop(i)
            salvar_dados(CLIENTES_FILE, clientes)
            return cliente
    raise HTTPException(status_code=404, detail="Cliente não encontrado")

@app.put("/clientes/{cliente_id}", response_model=Cliente)
async def editar_cliente(cliente_id: int, cliente_atualizado: Cliente):
    for i, c in enumerate(clientes):
        if c.id == cliente_id:
            clientes[i] = cliente_atualizado
            salvar_dados(CLIENTES_FILE, clientes)
            return cliente_atualizado
    raise HTTPException(status_code=404, detail="Cliente não encontrado")

@app.delete("/reservas/{reserva_id}", response_model=Reserva)
async def cancelar_reserva(reserva_id: int):
    for i, r in enumerate(reservas):
        if r.id == reserva_id:
            reserva = reservas.pop(i)
            salvar_dados(RESERVAS_FILE, reservas)
            return reserva
    raise HTTPException(status_code=404, detail="Reserva não encontrada")

@app.put("/reservas/{reserva_id}", response_model=Reserva)
async def editar_reserva(reserva_id: int, reserva_atualizada: Reserva):
    for i, r in enumerate(reservas):
        if r.id == reserva_id:
            if not any(c.id == reserva_atualizada.cliente_id for c in clientes):
                raise HTTPException(status_code=404, detail="Cliente não encontrado")
            if not any(q.id == reserva_atualizada.quarto_id for q in quartos):
                raise HTTPException(status_code=404, detail="Quarto não encontrado")
            reservas[i] = reserva_atualizada
            salvar_dados(RESERVAS_FILE, reservas)
            return reserva_atualizada
    raise HTTPException(status_code=404, detail="Reserva não encontrada")

@app.delete("/quartos/{quarto_id}", response_model=Quarto)
async def remover_quarto(quarto_id: int):
    for i, q in enumerate(quartos):
        if q.id == quarto_id:
            quarto = quartos.pop(i)
            salvar_dados(QUARTOS_FILE, quartos)
            return quarto
    raise HTTPException(status_code=404, detail="Quarto não encontrado")

@app.put("/quartos/{quarto_id}", response_model=Quarto)
async def editar_quarto(quarto_id: int, quarto: Quarto):
    for i, q in enumerate(quartos):
        if q.id == quarto_id:
            quartos[i] = quarto
            salvar_dados(QUARTOS_FILE, quartos)
            return quarto
    raise HTTPException(status_code=404, detail="Quarto não encontrado")

@app.post("/itens/", response_model=Item)
async def adicionar_item(item: Item):
    global next_item_id
    item.id = next_item_id
    itens.append(item)
    next_item_id += 1
    salvar_dados(ITENS_FILE, itens)
    return item

@app.delete("/itens/{item_id}", response_model=Item)
async def remover_item(item_id: int):
    for i, item in enumerate(itens):
        if item.id == item_id:
            item_removido = itens.pop(i)
            salvar_dados(ITENS_FILE, itens)
            return item_removido
    raise HTTPException(status_code=404, detail="Item não encontrado")

@app.put("/itens/{item_id}", response_model=Item)
async def editar_item(item_id: int, item_atualizado: Item):
    for i, item in enumerate(itens):
        if item.id == item_id:
            itens[i] = item_atualizado
            salvar_dados(ITENS_FILE, itens)
            return item_atualizado
    raise HTTPException(status_code=404, detail="Item não encontrado")

@app.post("/compras/", response_model=Compra)
async def comprar_item(compra: Compra):
    global next_compra_id
    if not any(c.id == compra.cliente_id for c in clientes):
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if not any(i.id == compra.item_id for i in itens):
        raise HTTPException(status_code=404, detail="Item não encontrado")
    compra.id = next_compra_id
    compras.append(compra)
    next_compra_id += 1
    salvar_dados(COMPRAS_FILE, compras)
    return compra

@app.get("/dados_hotel/")
async def exibir_dados_hotel():
    return {
        "quartos": quartos,
        "clientes": clientes,
        "reservas": reservas,
        "itens": itens,
        "compras": compras
    }
