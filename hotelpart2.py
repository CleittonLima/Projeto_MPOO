from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

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

#CRIAR PARA EDITAR E EXCLUIR QUARTO

@app.post("/clientes/", response_model=Cliente)
async def registrar_cliente(cliente: Cliente, db: Session = Depends(get_db)):
    db_cliente = ClienteDB(nome=cliente.nome, cpf=cliente.cpf)
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

#CRIAR PARA EDITAR E EXCLUIR CLIENTE

@app.post("/reservas/", response_model=Reserva)
async def fazer_reserva(reserva: Reserva, db: Session = Depends(get_db)):
    db_reserva = ReservaDB(cliente_id=reserva.cliente_id, quarto_id=reserva.quarto_id)
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

#CRIAR PARA EDITAR E EXCLUIR RESERVA

@app.post("/itens/", response_model=Item)
async def adicionar_item(item: Item, db: Session = Depends(get_db)):
    db_item = ItemDB(nome=item.nome, preco=item.preco)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

#CRIAR PARA EDITAR E EXCLUIR ITEM

@app.post("/compras/", response_model=Compra)
async def comprar_item(compra: Compra, db: Session = Depends(get_db)):
    db_compra = CompraDB(cliente_id=compra.cliente_id, item_id=compra.item_id)
    db.add(db_compra)
    db.commit()
    db.refresh(db_compra)
    return db_compra

#CRIAR PARA EDITAR E EXCLUIR COMPRA

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