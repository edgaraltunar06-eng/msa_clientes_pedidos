from infrastructure.database.mysql_repo import MySQLClienteRepository

class ClienteUseCases:
    def __init__(self):
        self.repo = MySQLClienteRepository()

    def crear_cliente(self, datos_cliente):
        nuevo_id = self.repo.guardar(datos_cliente)
        return {"id_cliente": nuevo_id, **datos_cliente}

    def obtener_cliente(self, id_cliente):
        return self.repo.obtener_por_id(id_cliente)

    def actualizar_cliente(self, id_cliente, datos_cliente):
        exito = self.repo.actualizar(id_cliente, datos_cliente)
        if exito:
            return self.repo.obtener_por_id(id_cliente)
        return None

    def eliminar_cliente(self, id_cliente):
        return self.repo.eliminar(id_cliente)