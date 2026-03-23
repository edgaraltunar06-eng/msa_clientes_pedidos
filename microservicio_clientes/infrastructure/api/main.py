from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import json
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.messaging.rpc_client import RpcClient

app = FastAPI(title="Microservicio de Clientes")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite cualquier origen en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
rpc = RpcClient()

# Modelo para Crear (Todos obligatorios o con valores por defecto)
class Cliente(BaseModel):
    nombre: str
    telefono: str
    email: str

# Modelo para Actualizar (Todos opcionales para permitir actualizaciones parciales)
class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None

@app.post("/clientes/")
async def crear_cliente(cliente: Cliente):
    payload = {
        "accion": "crear_cliente",
        "datos": cliente.model_dump()
    }
    respuesta = rpc.call(json.dumps(payload), 'rpc_queue_clientes')
    return respuesta

@app.get("/clientes/{id_cliente}")
async def obtener_cliente(id_cliente: int):
    payload = {
        "accion": "obtener_cliente",
        "datos": {"id": id_cliente}
    }
    respuesta = rpc.call(json.dumps(payload), 'rpc_queue_clientes')
    return respuesta

@app.put("/clientes/{id_cliente}")
async def actualizar_cliente(id_cliente: int, cliente: ClienteUpdate):
    payload = {
        "accion": "actualizar_cliente",
        "datos": {
            "id": id_cliente,
            # exclude_unset ignora los campos que no se enviaron en el request
            "cliente": cliente.model_dump(exclude_unset=True) 
        }
    }
    respuesta = rpc.call(json.dumps(payload), 'rpc_queue_clientes')
    return respuesta

@app.delete("/clientes/{id_cliente}")
async def eliminar_cliente(id_cliente: int):
    payload = {
        "accion": "eliminar_cliente",
        "datos": {"id": id_cliente}
    }
    respuesta = rpc.call(json.dumps(payload), 'rpc_queue_clientes')
    return respuesta