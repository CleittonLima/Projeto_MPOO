from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

DATABASE_URL = "sqlite:///./hotel.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class QuartoDB(Base):
    __tablename__ = "quartos"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, index=True)
    tipo = Column(String)
    preco = Column(Float)

class ClienteDB(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    cpf = Column(Integer, unique=True, index=True)

class ReservaDB(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    quarto_id = Column(Integer, ForeignKey("quartos.id"))

class ItemDB(Base):
    __tablename__ = "itens"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    preco = Column(Float)

class CompraDB(Base):
    __tablename__ = "compras"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    item_id = Column(Integer, ForeignKey("itens.id"))

Base.metadata.create_all(bind=engine)

# Classes
class Quarto(BaseModel):
    id: int
    numero: str
    tipo: str
    preco: float

    class Config:
        orm_mode = True

class Cliente(BaseModel):
    id: int
    nome: str
    cpf: int

    class Config:
        orm_mode = True

class Reserva(BaseModel):
    id: int
    cliente_id: int
    quarto_id: int

    class Config:
        orm_mode = True

class Item(BaseModel):
    id: int
    nome: str
    preco: float

    class Config:
        orm_mode = True

class Compra(BaseModel):
    id: int
    cliente_id: int
    item_id: int

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# Endpoints
@app.post("/quartos/", response_model=Quarto)
async def adicionar_quarto(quarto: Quarto, db: Session = Depends(get_db)):
    db_quarto = QuartoDB(numero=quarto.numero, tipo=quarto.tipo, preco=quarto.preco)
    db.add(db_quarto)
    db.commit()
    db.refresh(db_quarto)
    return db_quarto

@app.put("/quartos/{quarto_id}", response_model=Quarto)
async def editar_quarto(quarto_id: int, quarto_atualizado: Quarto, db: Session = Depends(get_db)):
    quarto = db.query(QuartoDB).filter(QuartoDB.id == quarto_id).first()
    if not quarto:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")
    quarto.numero = quarto_atualizado.numero
    quarto.tipo = quarto_atualizado.tipo
    quarto.preco = quarto_atualizado.preco
    db.commit()
    db.refresh(quarto)
    return quarto

@app.delete("/quartos/{quarto_id}", response_model=Quarto)
async def remover_quarto(quarto_id: int, db: Session = Depends(get_db)):
    quarto = db.query(QuartoDB).filter(QuartoDB.id == quarto_id).first()
    if not quarto:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")
    db.delete(quarto)
    db.commit()
    return quarto

@app.post("/clientes/", response_model=Cliente)
async def registrar_cliente(cliente: Cliente, db: Session = Depends(get_db)):
    db_cliente = ClienteDB(nome=cliente.nome, cpf=cliente.cpf)
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@app.put("/clientes/{cliente_id}", response_model=Cliente)
async def editar_cliente(cliente_id: int, cliente_atualizado: Cliente, db: Session = Depends(get_db)):
    cliente = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    cliente.nome = cliente_atualizado.nome
    cliente.cpf = cliente_atualizado.cpf
    db.commit()
    db.refresh(cliente)
    return cliente

@app.delete("/clientes/{cliente_id}", response_model=Cliente)
async def remover_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    db.delete(cliente)
    db.commit()
    return cliente

@app.post("/reservas/", response_model=Reserva)
async def fazer_reserva(reserva: Reserva, db: Session = Depends(get_db)):
    db_reserva = ReservaDB(cliente_id=reserva.cliente_id, quarto_id=reserva.quarto_id)
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

@app.put("/reservas/{reserva_id}", response_model=Reserva)
async def editar_reserva(reserva_id: int, reserva_atualizada: Reserva, db: Session = Depends(get_db)):
    reserva = db.query(ReservaDB).filter(ReservaDB.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    reserva.cliente_id = reserva_atualizada.cliente_id
    reserva.quarto_id = reserva_atualizada.quarto_id
    db.commit()
    db.refresh(reserva)
    return reserva

@app.delete("/reservas/{reserva_id}", response_model=Reserva)
async def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(ReservaDB).filter(ReservaDB.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    db.delete(reserva)
    db.commit()
    return reserva

@app.post("/itens/", response_model=Item)
async def adicionar_item(item: Item, db: Session = Depends(get_db)):
    db_item = ItemDB(nome=item.nome, preco=item.preco)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/itens/{item_id}", response_model=Item)
async def editar_item(item_id: int, item_atualizado: Item, db: Session = Depends(get_db)):
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    item.nome = item_atualizado.nome
    item.preco = item_atualizado.preco
    db.commit()
    db.refresh(item)
    return item

@app.delete("/itens/{item_id}", response_model=Item)
async def remover_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(item)
    db.commit()
    return item

@app.post("/compras/", response_model=Compra)
async def comprar_item(compra: Compra, db: Session = Depends(get_db)):
    db_compra = CompraDB(cliente_id=compra.cliente_id, item_id=compra.item_id)
    db.add(db_compra)
    db.commit()
    db.refresh(db_compra)
    return db_compra

@app.get("/dados_hotel/")
async def exibir_dados_hotel(db: Session = Depends(get_db)):
    quartos = db.query(QuartoDB).all()
    clientes = db.query(ClienteDB).all()
    reservas = db.query(ReservaDB).all()
    itens = db.query(ItemDB).all()
    compras = db.query(CompraDB).all()
    return {
        "quartos": quartos,
        "clientes": clientes,
        "reservas": reservas,
        "itens": itens,
        "compras": compras
    }