import psycopg2

class PostgresPedidoRepository:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="pedidos_db",
            user="admin",
            password="secretpassword",
            host="localhost",
            port="5434"
        )
        self.cursor = self.conn.cursor()
        self._crear_tabla()

    def _crear_tabla(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id_pedido SERIAL PRIMARY KEY,
                nombre_pedido VARCHAR(100) NOT NULL,
                cantidad INTEGER NOT NULL,
                id_cliente INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def guardar(self, pedido_dict):
        self.cursor.execute(
            "INSERT INTO pedidos (nombre_pedido, cantidad, id_cliente) VALUES (%s, %s, %s) RETURNING id_pedido",
            (pedido_dict['nombre_pedido'], pedido_dict['cantidad'], pedido_dict['id_cliente'])
        )
        new_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return new_id

    def obtener_por_id(self, id_pedido):
        self.cursor.execute("SELECT id_pedido, nombre_pedido, cantidad, id_cliente FROM pedidos WHERE id_pedido = %s", (id_pedido,))
        row = self.cursor.fetchone()
        if row:
            return {"id_pedido": row[0], "nombre_pedido": row[1], "cantidad": row[2], "id_cliente": row[3]}
        return None

    def actualizar(self, id_pedido, pedido_dict):
        if not pedido_dict:
            return False

        set_clause = ", ".join([f"{key} = %s" for key in pedido_dict.keys()])
        valores = list(pedido_dict.values())
        valores.append(id_pedido)

        query = f"UPDATE pedidos SET {set_clause} WHERE id_pedido = %s"
        
        self.cursor.execute(query, tuple(valores))
        filas_afectadas = self.cursor.rowcount
        self.conn.commit()
        return filas_afectadas > 0

    def eliminar(self, id_pedido):
        self.cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s", (id_pedido,))
        filas_afectadas = self.cursor.rowcount
        self.conn.commit()
        return filas_afectadas > 0