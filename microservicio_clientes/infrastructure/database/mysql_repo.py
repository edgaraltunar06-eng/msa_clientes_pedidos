import pymysql

class MySQLClienteRepository:
    def __init__(self):
        self.conn = pymysql.connect(
            host="localhost",
            port=3307,
            user="root",
            password="rootpassword",
            database="clientes_db",
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()
        self._crear_tabla()

    def _crear_tabla(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                telefono VARCHAR(20),
                email VARCHAR(100) UNIQUE
            )
        """)
        self.conn.commit()

    def guardar(self, cliente_dict):
        self.cursor.execute(
            "INSERT INTO clientes (nombre, telefono, email) VALUES (%s, %s, %s)",
            (cliente_dict['nombre'], cliente_dict['telefono'], cliente_dict['email'])
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def obtener_por_id(self, id_cliente):
        self.cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id_cliente,))
        return self.cursor.fetchone()

    def actualizar(self, id_cliente, cliente_dict):
        # Si el diccionario llega vacío, no hay nada que actualizar
        if not cliente_dict:
            return False

        # Construcción dinámica del query SQL para actualizaciones parciales
        set_clause = ", ".join([f"{key} = %s" for key in cliente_dict.keys()])
        valores = list(cliente_dict.values())
        valores.append(id_cliente)

        query = f"UPDATE clientes SET {set_clause} WHERE id_cliente = %s"
        
        self.cursor.execute(query, tuple(valores))
        filas_afectadas = self.cursor.rowcount
        self.conn.commit()
        return filas_afectadas > 0

    def eliminar(self, id_cliente):
        self.cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
        filas_afectadas = self.cursor.rowcount
        self.conn.commit()
        return filas_afectadas > 0