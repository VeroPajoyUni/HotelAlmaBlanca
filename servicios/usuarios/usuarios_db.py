import os
import time

import psycopg
from psycopg.rows import dict_row


# ---------- Conexión a PostgreSQL (reintenta mientras la base de datos arranca) ----------
def conectar():
    for intento in range(10):
        try:
            return psycopg.connect(
                host=os.getenv("USUARIOS_DB_HOST"),
                port=int(os.getenv("USUARIOS_DB_PORT", "5432")),
                user=os.getenv("USUARIOS_DB_USER"),
                password=os.getenv("USUARIOS_DB_PASSWORD"),
                dbname=os.getenv("USUARIOS_DB_NAME"),
                row_factory=dict_row,
                connect_timeout=5
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
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nombre VARCHAR(80) NOT NULL,
            apellido VARCHAR(80) NOT NULL,
            documento VARCHAR(30) NOT NULL UNIQUE,
            email VARCHAR(150) NOT NULL UNIQUE,
            telefono VARCHAR(25) NOT NULL,
            rol VARCHAR(20) NOT NULL DEFAULT 'cliente' CHECK (rol IN ('cliente', 'recepcionista', 'administrador')),
            fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        INSERT INTO usuarios (nombre, apellido, documento, email, telefono, rol)
        VALUES
            ('Ana', 'Perez', '1001001001', 'ana@example.com', '3001234567', 'cliente'),
            ('Carlos', 'Lopez', '1001001002', 'carlos@example.com', '3109876543', 'cliente'),
            ('Laura', 'Gomez', '1001001003', 'laura@example.com', '3201234567', 'recepcionista'),
            ('Andres', 'Torres', '1001001004', 'andres@example.com', '3159876543', 'administrador')
        ON CONFLICT DO NOTHING
    """)
    conexion.commit()
    cursor.close()
    conexion.close()

# Para revisar la base de datos manualmente:
# docker compose exec usuarios-db psql -U usuarios -d usuarios
