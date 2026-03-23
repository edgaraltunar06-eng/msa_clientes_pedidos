import pika
import uuid
import json

class RpcClient:
    def __init__(self):
        credentials = pika.PlainCredentials('admin', 'secretpassword')
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost', credentials=credentials)
        )
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n, routing_key):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key=routing_key,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=n
        )
        while self.response is None:
            self.connection.process_data_events(time_limit=None)
        return json.loads(self.response)