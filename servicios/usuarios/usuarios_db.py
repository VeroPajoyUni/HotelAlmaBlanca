import os

import psycopg
from psycopg.rows import dict_row


def conectar():
    conexion = psycopg.connect(
        host=os.getenv("USUARIOS_DB_HOST"),
        port=int(os.getenv("USUARIOS_DB_PORT", "5432")),
        user=os.getenv("USUARIOS_DB_USER"),
        password=os.getenv("USUARIOS_DB_PASSWORD"),
        dbname=os.getenv("USUARIOS_DB_NAME"),
        row_factory=dict_row,
        connect_timeout=5
    )

    return conexion

# docker exec -it hotelalmablanca-usuarios-db-1 bash
# psql -U usurios -W

# docker compose exec usuarios-db psql -U usuarios -d usuarios

'''
CREATE TABLE usuarios (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    apellido VARCHAR(80) NOT NULL,
    documento VARCHAR(30) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(25) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'cliente' CHECK (rol IN ('cliente', 'recepcionista', 'administrador')),
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO usuarios
(nombre, apellido, documento, email, telefono, rol)
VALUES 
('Ana', 'Perez', '1001001001', 'ana@example.com', '3001234567', 'cliente'),
('Carlos', 'Lopez', '1001001002', 'carlos@example.com', '3109876543', 'cliente'),
('Laura', 'Gomez', '1001001003', 'laura@example.com', '3201234567', 'recepcionista'),
('Andres', 'Torres', '1001001004', 'andres@example.com', '3159876543', 'administrador');

'''