import os
import time

# Conector para PostgreSQL
import psycopg


# ---------- Conexión a PostgreSQL (reintenta mientras la base de datos arranca) ----------
def conectar():
    for intento in range(10):
        try:
            conexion = psycopg.connect(
                host=os.getenv("RESERVAS_DB_HOST"),
                port=int(os.getenv("RESERVAS_DB_PORT", "5432")),
                user=os.getenv("RESERVAS_DB_USER"),
                password=os.getenv("RESERVAS_DB_PASSWORD"),
                dbname=os.getenv("RESERVAS_DB_NAME"),
            )
            return conexion
        except psycopg.OperationalError:
            print(f"La base de datos se está conectando... intento {intento + 1}.")
            if intento == 9:
                raise
            time.sleep(3)


# ---------- Creación de la tabla y reserva de ejemplo (solo si no existen) ----------
def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            usuario_id INTEGER,
            habitacion_id INTEGER,
            fecha_entrada DATE,
            fecha_salida DATE,
            huespedes INTEGER,
            estado VARCHAR(20) DEFAULT 'pendiente'
        )
    """)
    cursor.execute("""
        INSERT INTO reservas (usuario_id, habitacion_id, fecha_entrada, fecha_salida, huespedes)
        SELECT 1, 1, '2026-12-20', '2026-12-23', 2
        WHERE NOT EXISTS (SELECT 1 FROM reservas)
    """)
    conexion.commit()
    cursor.close()
    conexion.close()

# Para revisar la base de datos manualmente:
# docker compose exec reservas-db psql -U reservas -d reservas
#   \dt           -- listar las tablas
#   \d reservas   -- ver las columnas de la tabla
