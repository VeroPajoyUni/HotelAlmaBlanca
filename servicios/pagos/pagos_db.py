import os
import time
import psycopg

def conectar():
    for intento in range(10):
        try:
            conexion = psycopg.connect(
                host=os.getenv("PAGOS_DB_HOST"),
                port=int(os.getenv("PAGOS_DB_PORT", "5432")),
                user=os.getenv("PAGOS_DB_USER"),
                password=os.getenv("PAGOS_DB_PASSWORD"),
                dbname=os.getenv("PAGOS_DB_NAME"),
            )
            return conexion

        except psycopg.OperationalError:
            print(
                f"La base de datos se está conectando... "
                f"intento {intento + 1}."
            )
            if intento == 9:
                raise
            time.sleep(3)


def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            reserva_id BIGINT NOT NULL,
            monto NUMERIC(12, 2) NOT NULL
                CHECK (monto > 0),
            metodo_pago VARCHAR(30) NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                CHECK (estado IN (
                    'pendiente',
                    'pagado',
                    'rechazado'
                )),
            fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conexion.commit()
    cursor.close()
    conexion.close()
