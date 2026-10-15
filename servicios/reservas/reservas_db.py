import os
import time

# Conector para PostgreSQL
import psycopg

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

# docker exec -it hotelalmablanca-reservas-db-1 bash
# psql -U reservas -W

# \l                 -- listar las bases de datos
# \c reservas        -- conectarse a reservas
# \dt                -- listar las tablas
# \d reservas        -- ver las columnas y propiedades de la tabla

'''
CREATE TABLE IF NOT EXISTS reservas (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id INTEGER,
    habitacion_id INTEGER,
    fecha_entrada DATE,
    fecha_salida DATE,
    huespedes INTEGER,
    estado VARCHAR(20) DEFAULT 'pendiente'
);

INSERT INTO reservas (usuario_id, habitacion_id, fecha_entrada, fecha_salida, huespedes)
SELECT 1, 1, '2026-12-20', '2026-12-23', 2 
WHERE NOT EXISTS (
    SELECT 1
    FROM reservas
    WHERE usuario_id = 1
      AND habitacion_id = 1
      AND fecha_entrada = '2026-12-20'
      AND fecha_salida = '2026-12-23'
);
'''