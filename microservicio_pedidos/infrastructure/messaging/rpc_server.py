import pika
import json
from application.use_cases import PedidoUseCases

casos_uso = PedidoUseCases()

credentials = pika.PlainCredentials('admin', 'secretpassword')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', credentials=credentials)
)
channel = connection.channel()

channel.queue_declare(queue='rpc_queue_pedidos')

def procesar_peticion(payload):
    accion = payload.get("accion")
    datos = payload.get("datos")

    try:
        if accion == "crear_pedido":
            resultado = casos_uso.crear_pedido(datos)
            return {"status": "exito", "data": resultado}
            
        elif accion == "obtener_pedido":
            resultado = casos_uso.obtener_pedido(datos.get("id"))
            if resultado:
                return {"status": "exito", "data": resultado}
            return {"status": "error", "mensaje": "Pedido no encontrado"}
            
        elif accion == "actualizar_pedido":
            resultado = casos_uso.actualizar_pedido(datos.get("id"), datos.get("pedido"))
            if resultado:
                return {"status": "exito", "data": resultado}
            return {"status": "error", "mensaje": "Pedido no encontrado o sin cambios"}
            
        elif accion == "eliminar_pedido":
            exito = casos_uso.eliminar_pedido(datos.get("id"))
            if exito:
                return {"status": "exito", "mensaje": "Pedido eliminado exitosamente"}
            return {"status": "error", "mensaje": "Pedido no encontrado"}
            
        else:
            return {"status": "error", "mensaje": "Acción no reconocida"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def on_request(ch, method, props, body):
    payload = json.loads(body)
    respuesta = procesar_peticion(payload)

    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps(respuesta)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue_pedidos', on_message_callback=on_request)

channel.start_consuming()