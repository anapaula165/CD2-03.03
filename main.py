from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(
    title="Bella Tavola API",
    description="API do restaurante Bella Tavola",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "restaurante": "Bella Tavola",
        "mensagem": "Bem-vindo à nossa API",
        "chefe": "Ana Linda",
        "cidade": "Roma",
        "especialidade": "Pizza Mamma Mia"
    }

# Adicionando pratos no cardápio
pratos = [
    {"id": 1, "nome": "Parma", "categoria": "pizza", "preco": 60.0, "disponivel": False},
    {"id": 2, "nome": "Carbonara", "categoria": "massa", "preco": 55.0, "disponivel": False},
    {"id": 3, "nome": "Lasanha Quatro Queijos", "categoria": "massa", "preco": 70.0, "disponivel": True},
    {"id": 4, "nome": "Gelatto Sabores", "categoria": "sobremesa", "preco": 28.0, "disponivel": True},
    {"id": 5, "nome": "Napolitana", "categoria": "pizza", "preco": 80.0, "disponivel": True},
    {"id": 6, "nome": "Banoffee", "categoria": "sobremesa", "preco": 24.0, "disponivel": True},
]

#Filtrando pratos

@app.get("/pratos/{prato_id}")
async def buscar_prato(prato_id: int, formato: str = "completo"):
    for prato in pratos:
        if prato["id"] == prato_id:
            if formato == "resumido":
                return {"nome": prato["nome"], "preco": prato["preco"]}
            return prato
    return {"mensagem": "Prato não encontrado"}

@app.get("/pratos")
async def listar_pratos(
    categoria: Optional[str] = None,
    preco_maximo: Optional[float] = None,
    apenas_disponiveis: bool = False
):
    resultado = pratos
    if categoria:
        resultado = [p for p in resultado if p["categoria"] == categoria]
    if preco_maximo:
        resultado = [p for p in resultado if p["preco"] <= preco_maximo]
    if apenas_disponiveis:
        resultado = [p for p in resultado if p["disponivel"]]
    return resultado

#Adicionando um prato novo

# Separando informações de entrada e saída
# Para evitar expor campos como "id" e "criado_em" na entrada, criamos modelos separados para entrada e saída dos dados. 
# o INPUT já tinha testado criando o prato BALA

class PratoInput(BaseModel):
    nome: str
    categoria: str
    preco: float
    descricao: Optional[str] = None
    disponivel: bool = True

class PratoOutput(BaseModel):
    id: int
    nome: str
    categoria: str
    preco: float
    descricao: Optional[str]
    disponivel: bool
    criado_em: str

@app.post("/pratos", response_model=PratoOutput)
async def criar_prato(prato: PratoInput):
    novo_id = max(p["id"] for p in pratos) + 1
    novo_prato = {
        "id": novo_id,
        "criado_em": datetime.now().isoformat(),
        **prato.model_dump()
    }
    pratos.append(novo_prato)
    return novo_prato

# DESAFIO DAS BEBIDAS - Colocando bebidas no cardápio - API

bebidas = [
    {"id": 1, "nome": "Água Mineral", "tipo": "agua", "preco": 8.0, "alcoolica": False, "volume_ml": 500, "criado_em": "2024-01-01T00:00:00"},
    {"id": 2, "nome": "Pérgola", "tipo": "vinho", "preco": 24.0, "alcoolica": True, "volume_ml": 750, "criado_em": "2024-01-01T00:00:00"},
    {"id": 3, "nome": "Pedra Salgado", "tipo": "agua", "preco": 15.0, "alcoolica": False, "volume_ml": 750, "criado_em": "2024-01-01T00:00:00"},
    {"id": 4, "nome": "Suco de Laranja", "tipo": "suco", "preco": 18.0, "alcoolica": False, "volume_ml": 300, "criado_em": "2024-01-01T00:00:00"},
    {"id": 5, "nome": "Prosecco Frisante", "tipo": "vinho", "preco": 200.0, "alcoolica": True, "volume_ml": 750, "criado_em": "2024-01-01T00:00:00"},
    {"id": 6, "nome": "Coca-Cola", "tipo": "refrigerante", "preco": 12.0, "alcoolica": False, "volume_ml": 350, "criado_em": "2024-01-01T00:00:00"},
]

class BebidaInput(BaseModel):
    nome: str
    tipo: str
    preco: float
    alcoolica: bool
    volume_ml: int

class BebidaOutput(BaseModel):
    id: int
    nome: str
    tipo: str
    preco: float
    alcoolica: bool
    volume_ml: int
    criado_em: str

@app.get("/bebidas")
async def listar_bebidas(
    tipo: Optional[str] = None,
    alcoolica: Optional[bool] = None
):
    resultado = bebidas
    if tipo:
        resultado = [b for b in resultado if b["tipo"] == tipo]
    if alcoolica is not None:
        resultado = [b for b in resultado if b["alcoolica"] == alcoolica]
    return resultado

@app.get("/bebidas/{bebida_id}")
async def buscar_bebida(bebida_id: int):
    for bebida in bebidas:
        if bebida["id"] == bebida_id:
            return bebida
    return {"mensagem": "Bebida não encontrada"}

@app.post("/bebidas", response_model=BebidaOutput)
async def criar_bebida(bebida: BebidaInput):
    novo_id = max(b["id"] for b in bebidas) + 1
    nova_bebida = {
        "id": novo_id,
        "criado_em": datetime.now().isoformat(),
        **bebida.model_dump()
    }
    bebidas.append(nova_bebida)
    return nova_bebida
