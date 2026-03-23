from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.messaging.rpc_clients import RpcClient

app = FastAPI(title="Microservicio de Pedidos")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite cualquier origen en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
rpc = RpcClient()

class Pedido(BaseModel):
    nombre_pedido: str
    cantidad: int
    id_cliente: int

class PedidoUpdate(BaseModel):
    nombre_pedido: Optional[str] = None
    cantidad: Optional[int] = None
    id_cliente: Optional[int] = None

@app.post("/pedidos/")
async def crear_pedido(pedido: Pedido):
    # PASO 1: Validar si el cliente existe comunicándose con el otro microservicio
    payload_validacion = {
        "accion": "verificar_cliente",
        "datos": {"id": pedido.id_cliente}
    }
    # Mandamos el mensaje a la cola de CLIENTES
    respuesta_cliente = rpc.call(json.dumps(payload_validacion), 'rpc_queue_clientes')

    # Evaluamos la respuesta del Worker de Clientes
    if respuesta_cliente.get("status") == "exito" and respuesta_cliente.get("existe") is True:
        # PASO 2: El cliente existe, procedemos a guardar el pedido
        payload_pedido = {
            "accion": "crear_pedido",
            "datos": pedido.model_dump()
        }
        # Mandamos el mensaje a la cola de PEDIDOS
        respuesta_final = rpc.call(json.dumps(payload_pedido), 'rpc_queue_pedidos')
        return respuesta_final
    else:
        # El cliente no existe, detenemos el proceso y devolvemos un error 400
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede crear el pedido. El id_cliente {pedido.id_cliente} no existe en la base de datos."
        )

@app.get("/pedidos/{id_pedido}")
async def obtener_pedido(id_pedido: int):
    payload = {
        "accion": "obtener_pedido",
        "datos": {"id": id_pedido}
    }
    respuesta = rpc.call(json.dumps(payload), 'rpc_queue_pedidos')
    return respuesta

@app.put("/pedidos/{id_pedido}")
async def actualizar_pedido(id_pedido: int, pedido: PedidoUpdate):
    # Opcional: Podrías aplicar la misma validación aquí si permites actualizar el id_cliente
    if pedido.id_cliente is not None:
        payload_validacion = {
            "accion": "verificar_cliente",
            "datos": {"id": pedido.id_cliente}
        }
        respuesta_cliente = rpc.call(json.dumps(payload_validacion), 'rpc_queue_clientes')
        if not (respuesta_cliente.get("status") == "exito" and respuesta_cliente.get("existe") is True):
            raise HTTPException(status_code=400, detail="El nuevo id_cliente no existe.")

    payload = {
        "accion": "actualizar_pedido",
        "datos": {
            "id": id_pedido,
            "pedido": pedido.model_dump(exclude_unset=True)
        }
    }
    respuesta = rpc.call(json.dumps(payload), 'rpc_queue_pedidos')
    return respuesta

@app.delete("/pedidos/{id_pedido}")
async def eliminar_pedido(id_pedido: int):
    payload = {
        "accion": "eliminar_pedido",
        "datos": {"id": id_pedido}
    }
    respuesta = rpc.call(json.dumps(payload), 'rpc_queue_pedidos')
    return respuesta