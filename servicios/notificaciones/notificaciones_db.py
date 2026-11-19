import os
import time

import psycopg


def conectar():
    for intento in range(10):
        try:
            return psycopg.connect(
                host=os.getenv("NOTIFICACIONES_DB_HOST"),
                port=int(os.getenv("NOTIFICACIONES_DB_PORT", "5432")),
                user=os.getenv("NOTIFICACIONES_DB_USER"),
                password=os.getenv("NOTIFICACIONES_DB_PASSWORD"),
                dbname=os.getenv("NOTIFICACIONES_DB_NAME"),
            )
        except psycopg.OperationalError:
            print(
                "La base de datos de Notificaciones se está conectando... "
                f"intento {intento + 1}."
            )
            if intento == 9:
                raise
            time.sleep(3)


def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notificaciones (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            mensaje TEXT NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                CHECK (estado IN ('pendiente', 'leida')),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conexion.commit()
    cursor.close()
    conexion.close()

'''
{
  "usuario_id":1,
  "tipo":"reserva",
  "mensaje":"Notificación de prueba"
}
'''