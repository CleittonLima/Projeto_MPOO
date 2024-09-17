from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./hotel.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BaseModelDB(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)


class QuartoDB(Base):
    __tablename__ = "quartos"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, index=True)
    tipo = Column(String)
    preco = Column(Float)
    reservas = relationship("ReservaDB", back_populates="quarto")

class ClienteDB(BaseModelDB):
    __tablename__ = "clientes"
    nome = Column(String)
    cpf = Column(Integer, unique=True, index=True)
    reservas = relationship("ReservaDB", back_populates="cliente")
    compras = relationship("CompraDB", back_populates="cliente")


class ReservaDB(BaseModelDB):
    __tablename__ = "reservas"
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    quarto_id = Column(Integer, ForeignKey("quartos.id"))
    dias = Column(Integer)
    cliente = relationship("ClienteDB", back_populates="reservas")
    quarto = relationship("QuartoDB", back_populates="reservas")

class ItemDB(BaseModelDB):
    __tablename__ = "itens"
    nome = Column(String)
    preco = Column(Float)
    compras = relationship("CompraDB", back_populates="item")


class CompraDB(BaseModelDB):
    __tablename__ = "compras"
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    item_id = Column(Integer, ForeignKey("itens.id"))
    cliente = relationship("ClienteDB", back_populates="compras")
    item = relationship("ItemDB", back_populates="compras")

Base.metadata.create_all(bind=engine)

class Quarto(BaseModel):
    id: int
    numero: str
    tipo: str
    preco: float = Field(gt=0, description="Preço deve ser maior que 0")

    class Config:
        orm_mode = True

class Cliente(BaseModel):
    id: int
    nome: str
    cpf: int = Field(..., title="CPF", description="Deve ter 11 dígitos")

    @validator('cpf')
    def validar_cpf(cls, v):
        if len(str(v)) != 11:
            raise ValueError('CPF deve ter exatamente 11 dígitos')
        return v

    class Config:
        orm_mode = True

class Reserva(BaseModel):
    id: int
    cliente_id: int
    quarto_id: int
    dias: int = Field(gt=0, description="Número de dias de hospedagem deve ser maior que 0")

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
    db_reserva = ReservaDB(cliente_id=reserva.cliente_id, quarto_id=reserva.quarto_id, dias=reserva.dias)
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
    reserva.dias = reserva_atualizada.dias
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

@app.get("/clientes/{cliente_id}/reservas")
async def listar_reservas_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    reservas = db.query(ReservaDB).filter(ReservaDB.cliente_id == cliente_id).all()
    if not reservas:
        raise HTTPException(status_code=404, detail="Nenhuma reserva encontrada para este cliente")
    return reservas

@app.get("/total_pagar/{cliente_id}", response_model=dict)
async def calcular_nota_fiscal(cliente_id: int, db: Session = Depends(get_db)):
    reservas = db.query(ReservaDB).filter(ReservaDB.cliente_id == cliente_id).all()
    if not reservas:
        raise HTTPException(status_code=404, detail="Nenhuma reserva encontrada para o cliente")

    total_reservas = 0
    reservas_detalhadas = []

    for reserva in reservas:
        quarto = db.query(QuartoDB).filter(QuartoDB.id == reserva.quarto_id).first()
        if quarto:
            preco_total = quarto.preco * reserva.dias
            total_reservas += preco_total
            reservas_detalhadas.append({
                "quarto": quarto.tipo,
                "dias": reserva.dias,
                "preco_diaria": quarto.preco,
                "preco_total": preco_total
            })

    compras = db.query(CompraDB).filter(CompraDB.cliente_id == cliente_id).all()
    total_compras = 0
    itens_comprados = []

    for compra in compras:
        item = db.query(ItemDB).filter(ItemDB.id == compra.item_id).first()
        if item:
            total_compras += item.preco
            itens_comprados.append({
                "nome": item.nome,
                "preco": item.preco
            })

    total_a_pagar = total_reservas + total_compras
    cliente = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    return {
        "nome_cliente": cliente.nome,
        "reservas": reservas_detalhadas,
        "itens_comprados": itens_comprados,
        "total_reservas": total_reservas,
        "total_compras": total_compras,
        "total_a_pagar": total_a_pagar
    }

@app.get("/dados_hotel/")
async def exibir_dados_hotel(db: Session = Depends(get_db)):
    quartos = db.query(QuartoDB).all()
    clientes = db.query(ClienteDB).all()
    reservas = db.query(ReservaDB).all()
    itens = db.query(ItemDB).all()
    compras = db.query(CompraDB).all()

    dados_hotel = {
        "quartos": quartos,
        "clientes": clientes,
        "reservas": reservas,
        "itens": itens,
        "compras": compras
    }

    for cliente in clientes:
        reservas_cliente = db.query(ReservaDB).filter(ReservaDB.cliente_id == cliente.id).all()
        compras_cliente = db.query(CompraDB).filter(CompraDB.cliente_id == cliente.id).all()

        total_reservas = 0
        for reserva in reservas_cliente:
            quarto = db.query(QuartoDB).filter(QuartoDB.id == reserva.quarto_id).first()
            if quarto:
                total_reservas += quarto.preco * reserva.dias

        total_compras = 0
        for compra in compras_cliente:
            item = db.query(ItemDB).filter(ItemDB.id == compra.item_id).first()
            if item:
                total_compras += item.preco

        total_a_pagar = total_reservas + total_compras

        cliente.total_a_pagar = total_a_pagar

    return dados_hotel