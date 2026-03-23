from infrastructure.database.postgres_repo import PostgresPedidoRepository

class PedidoUseCases:
    def __init__(self):
        self.repo = PostgresPedidoRepository()

    def crear_pedido(self, datos_pedido):
        nuevo_id = self.repo.guardar(datos_pedido)
        return {"id_pedido": nuevo_id, **datos_pedido}

    def obtener_pedido(self, id_pedido):
        return self.repo.obtener_por_id(id_pedido)

    def actualizar_pedido(self, id_pedido, datos_pedido):
        exito = self.repo.actualizar(id_pedido, datos_pedido)
        if exito:
            return self.repo.obtener_por_id(id_pedido)
        return None

    def eliminar_pedido(self, id_pedido):
        return self.repo.eliminar(id_pedido)