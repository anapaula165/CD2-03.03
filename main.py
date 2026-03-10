from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from fastapi import FastAPI, HTTPException  
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


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
    raise HTTPException(
        status_code=404,
        detail=f"Prato com id {prato_id} não encontrado"
    )

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
    nome: str = Field(min_length=3, max_length=100)
    categoria: str = Field(pattern="^(pizza|massa|sobremesa|entrada|salada)$")
    preco: float = Field(gt=0)
    preco_promocional: Optional[float] = Field(default=None, gt=0)
    descricao: Optional[str] = Field(default=None, max_length=500)
    disponivel: bool = True

    @field_validator("preco_promocional")
    @classmethod
    def validar_preco_promocional(cls, v, info):
        if v is None:
            return v
        if "preco" not in info.data:
            return v

        preco_original = info.data["preco"]

        if v >= preco_original:
            raise ValueError("Preço promocional deve ser menor que o preço original")

        desconto = (preco_original - v) / preco_original
        if desconto > 0.5:
            raise ValueError("Desconto não pode ser maior que 50% do preço original")

        return v

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
    nome: str = Field(min_length=3, max_length=100)
    tipo: str = Field(pattern="^(vinho|agua|refrigerante|suco|cerveja)$")
    preco: float = Field(gt=0)
    alcoolica: bool
    volume_ml: int = Field(ge=50, le=2000)

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
    raise HTTPException(
        status_code=404,
        detail=f"Bebida com id {bebida_id} não encontrada"
    )

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

# Pedido e Disponibilidade do Prato

class DisponibilidadeInput(BaseModel):
    disponivel: bool

@app.put("/pratos/{prato_id}/disponibilidade")
async def alterar_disponibilidade(prato_id: int, body: DisponibilidadeInput):
    for prato in pratos:
        if prato["id"] == prato_id:
            prato["disponivel"] = body.disponivel
            return prato
    raise HTTPException(status_code=404, detail="Prato não encontrado")


pedidos = []

class PedidoInput(BaseModel):
    prato_id: int
    quantidade: int = Field(ge=1)
    observacao: Optional[str] = None

class PedidoOutput(BaseModel):
    id: int
    prato_id: int
    nome_prato: str
    quantidade: int
    valor_total: float
    observacao: Optional[str]

@app.post("/pedidos", response_model=PedidoOutput)
async def criar_pedido(pedido: PedidoInput):
    prato = next((p for p in pratos if p["id"] == pedido.prato_id), None)

    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")

    if not prato["disponivel"]:
        raise HTTPException(
            status_code=400,
            detail=f"O prato '{prato['nome']}' não está disponível no momento"
        )

    novo_id = len(pedidos) + 1
    novo_pedido = {
        "id": novo_id,
        "prato_id": pedido.prato_id,
        "nome_prato": prato["nome"],
        "quantidade": pedido.quantidade,
        "valor_total": prato["preco"] * pedido.quantidade,
        "observacao": pedido.observacao
    }
    pedidos.append(novo_pedido)
    return novo_pedido


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "erro": "Dados de entrada inválidos",
            "status": 422,
            "path": str(request.url),
            "detalhes": [
                {
                    "campo": " -> ".join(str(loc) for loc in e["loc"]),
                    "mensagem": e["msg"]
                }
                for e in exc.errors()
            ]
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "erro": exc.detail,
            "status": exc.status_code,
            "path": str(request.url),
            "detalhes": []
        }
    )


#Desafio API 2.0

# PROBLEMA 1: GET /reservas/{id} retorna 200 com {"erro": ...} quando não encontra
# PROBLEMA 2: POST aceita mesa=0, pessoas=0 ou negativos (sem validação com Field)
# PROBLEMA 3: DELETE não retorna nada (None implícito, status 200) quando não encontra
# PROBLEMA 4: listar_reservas compara bool com string "true" — nunca filtra corretamente
# PROBLEMA 5: POST não verifica se a mesa já está reservada

reservas = [
    {"id": 1, "mesa": 5, "nome": "Silva", "pessoas": 4, "ativa": True},
    {"id": 2, "mesa": 3, "nome": "Costa", "pessoas": 2, "ativa": False},
]

class ReservaInput(BaseModel):
    mesa: int = Field(ge=1, le=20)           # corrige problema 2
    nome: str = Field(min_length=2, max_length=100)
    pessoas: int = Field(ge=1, le=20)

@app.get("/reservas/{reserva_id}")
async def buscar_reserva(reserva_id: int):
    for r in reservas:
        if r["id"] == reserva_id:
            return r
    raise HTTPException(status_code=404, detail="Reserva não encontrada")  # corrige problema 1

@app.post("/reservas")
async def criar_reserva(reserva: ReservaInput):
    mesa_ocupada = any(                        # corrige problema 5
        r["mesa"] == reserva.mesa and r["ativa"]
        for r in reservas
    )
    if mesa_ocupada:
        raise HTTPException(
            status_code=400,
            detail=f"Mesa {reserva.mesa} já está reservada"
        )
    nova = {"id": len(reservas) + 1, **reserva.model_dump(), "ativa": True}
    reservas.append(nova)
    return nova

@app.delete("/reservas/{reserva_id}")
async def cancelar_reserva(reserva_id: int):
    for r in reservas:
        if r["id"] == reserva_id:
            r["ativa"] = False
            return {"mensagem": "Reserva cancelada com sucesso"}
    raise HTTPException(status_code=404, detail="Reserva não encontrada")  # corrige problema 3

@app.get("/reservas")
async def listar_reservas(apenas_ativas: bool = False):
    if apenas_ativas:
        return [r for r in reservas if r["ativa"]]  # corrige problema 4
    return reservas
