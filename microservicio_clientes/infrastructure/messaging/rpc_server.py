import pika
import json
from application.use_cases import ClienteUseCases

casos_uso = ClienteUseCases()

credentials = pika.PlainCredentials('admin', 'secretpassword')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', credentials=credentials)
)
channel = connection.channel()

channel.queue_declare(queue='rpc_queue_clientes')

def procesar_peticion(payload):
    accion = payload.get("accion")
    datos = payload.get("datos")

    try:
        if accion == "crear_cliente":
            resultado = casos_uso.crear_cliente(datos)
            return {"status": "exito", "data": resultado}
            
        elif accion == "obtener_cliente":
            resultado = casos_uso.obtener_cliente(datos.get("id"))
            if resultado:
                return {"status": "exito", "data": resultado}
            return {"status": "error", "mensaje": "Cliente no encontrado"}
            
        elif accion == "actualizar_cliente":
            resultado = casos_uso.actualizar_cliente(datos.get("id"), datos.get("cliente"))
            if resultado:
                return {"status": "exito", "data": resultado}
            return {"status": "error", "mensaje": "Cliente no encontrado o sin cambios"}
            
        elif accion == "eliminar_cliente":
            exito = casos_uso.eliminar_cliente(datos.get("id"))
            if exito:
                return {"status": "exito", "mensaje": "Cliente eliminado exitosamente"}
            return {"status": "error", "mensaje": "Cliente no encontrado"}
            
        # NUEVA ACCIÓN: Para validación cruzada con microservicio de pedidos
        elif accion == "verificar_cliente":
            resultado = casos_uso.obtener_cliente(datos.get("id"))
            if resultado:
                return {"status": "exito", "existe": True}
            return {"status": "exito", "existe": False}
            
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
channel.basic_consume(queue='rpc_queue_clientes', on_message_callback=on_request)

channel.start_consuming()