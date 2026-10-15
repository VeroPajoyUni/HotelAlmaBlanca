import os
import time

# Conector para PostgreSQL
import psycopg


# ---------- Conexión a PostgreSQL (reintenta mientras la base de datos arranca) ----------
def conectar():
    for intento in range(10):
        try:
            return psycopg.connect(
                host=os.getenv("HABITACIONES_DB_HOST"),
                port=int(os.getenv("HABITACIONES_DB_PORT", "5432")),
                user=os.getenv("HABITACIONES_DB_USER"),
                password=os.getenv("HABITACIONES_DB_PASSWORD"),
                dbname=os.getenv("HABITACIONES_DB_NAME"),
            )
        except psycopg.OperationalError:
            print(f"La base de datos se está conectando... intento {intento + 1}.")
            if intento == 9:
                raise
            time.sleep(3)


# ---------- Creación de la tabla y datos de ejemplo (solo si no existen) ----------
def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habitaciones (
            id           SERIAL PRIMARY KEY,
            numero       VARCHAR(10) NOT NULL UNIQUE,
            tipo         VARCHAR(20) NOT NULL CHECK (tipo IN ('sencilla', 'doble', 'suite')),
            capacidad    INTEGER NOT NULL CHECK (capacidad >= 1),
            precio_noche NUMERIC(10,2) NOT NULL CHECK (precio_noche >= 0),
            estado       VARCHAR(20) NOT NULL DEFAULT 'disponible' CHECK (estado IN ('disponible', 'ocupada', 'mantenimiento')),
            descripcion  VARCHAR(255)
        )
    """)
    cursor.execute("""
        INSERT INTO habitaciones (numero, tipo, capacidad, precio_noche, estado, descripcion)
        VALUES
            ('101', 'sencilla', 1, 90000.00, 'disponible', 'Cama sencilla, baño privado y TV'),
            ('102', 'doble', 2, 140000.00, 'disponible', 'Cama doble, baño privado y vista al patio'),
            ('201', 'doble', 3, 170000.00, 'ocupada', 'Cama doble y sencilla, balcón'),
            ('301', 'suite', 4, 320000.00, 'mantenimiento', 'Suite con sala y jacuzzi')
        ON CONFLICT DO NOTHING
    """)
    conexion.commit()
    cursor.close()
    conexion.close()

# Para revisar la base de datos manualmente:
# docker compose exec habitaciones-db psql -U habitaciones -d habitaciones
