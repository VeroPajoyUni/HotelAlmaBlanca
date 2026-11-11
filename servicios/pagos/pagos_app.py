
import os
from decimal import Decimal, InvalidOperation
from datetime import date
from email.utils import parsedate_to_datetime
from flask import Flask, jsonify, request
import requests
import pybreaker
from psycopg.rows import dict_row

from pagos_db import conectar, crear_tabla

reservas_url = os.getenv("RESERVAS_URL")

app = Flask(__name__)


circuito_reservas = pybreaker.CircuitBreaker(
    fail_max=int(os.getenv("CB_MAX_FALLOS", "3")),
    reset_timeout=int(os.getenv("CB_RECUPERACION", "30")),
    throw_new_error_on_trip=False,
)


@app.after_request
def permitir_cors(respuesta):
    respuesta.headers["Access-Control-Allow-Origin"] = "*"
    respuesta.headers["Access-Control-Allow-Headers"] = "Content-Type"
    respuesta.headers["Access-Control-Allow-Methods"] = (
        "GET, POST, PUT, PATCH, DELETE"
    )
    return respuesta

def consultar_reserva(id):
    timeout = int(os.getenv("RESERVAS_TIMEOUT", "2"))
    try:
        with circuito_reservas.calling():
            respuesta = requests.get(
                f"{reservas_url.rstrip('/')}/reservas/{id}/detalles",
                timeout=timeout,
            )
            if respuesta.status_code >= 500:
                respuesta.raise_for_status()
            datos = (
                respuesta.json()
                if respuesta.status_code == 200
                else None
            )

    except pybreaker.CircuitBreakerError:
        return None, (jsonify({"mensaje": "Circuito abierto: reservas no será consultado"}),503)
    except requests.exceptions.Timeout:
        return None, (jsonify({"mensaje": "El servicio de reservas tardó demasiado en responder"}),504)
    except requests.exceptions.ConnectionError:
        return None, (jsonify({"mensaje": "El servicio de reservas no está disponible"}),503)
    except requests.exceptions.HTTPError:
        return None, (jsonify({"mensaje": "Error del servidor de reservas"}), 502)
    except requests.exceptions.RequestException:
        return None, (jsonify({"mensaje": "Error al consultar el servicio de reservas"}),502)
    except ValueError:
        return None, (jsonify({"mensaje": "Respuesta inválida del servicio de reservas"}),502)

    if respuesta.status_code == 404:
        return None, (jsonify({"mensaje": "Reserva no encontrada"}),404 )
    if respuesta.status_code != 200:
        return None, (jsonify({"mensaje": "Respuesta inesperada del servicio de reservas"}),502)

    return datos, None

def calcular_total(reserva):

    def convertir_fecha(valor):
        try:
            return date.fromisoformat(valor)
        except ValueError:
            return parsedate_to_datetime(valor).date()

    fecha_entrada = convertir_fecha(
        reserva["fecha_entrada"]
    )

    fecha_salida = convertir_fecha(
        reserva["fecha_salida"]
    )

    noches = (fecha_salida - fecha_entrada).days

    if noches <= 0:
        raise ValueError("Fechas de reserva inválidas")

    precio_noche = Decimal(
        str(reserva["habitacion"]["precio_noche"])
    )

    if (
        not precio_noche.is_finite()
        or precio_noche <= 0
    ):
        raise ValueError("Precio de habitación inválido")

    total = precio_noche * noches

    return total

@app.route("/pagos/circuito", methods=["GET"])
def estado_circuito():
    return jsonify({
        "estado": circuito_reservas.current_state.upper(),
        "fallos_consecutivos": circuito_reservas.fail_counter,
        "umbral_fallos": circuito_reservas.fail_max,
        "periodo_recuperacion_s": circuito_reservas.reset_timeout,
    }), 200


@app.route("/pagos", methods=["GET"])
def listar():
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    cursor.execute("SELECT * FROM pagos ORDER BY id")
    pagos = cursor.fetchall()
    cursor.close()
    conexion.close()

    for pago in pagos:
        pago["monto"] = float(pago["monto"])

    return jsonify(pagos), 200

@app.route("/pagos/<int:id>", methods=["GET"])
def buscar(id):
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    cursor.execute(
        "SELECT * FROM pagos WHERE id = %s",(id,))

    pago = cursor.fetchone()
    cursor.close()
    conexion.close()

    if pago is None:
        return jsonify({"mensaje": "Pago no encontrado"}), 404
    pago["monto"] = float(pago["monto"])
    return jsonify(pago), 200


@app.route("/pagos", methods=["POST"])
def crear():
    nuevo_pago = request.get_json(silent=True)

    if not isinstance(nuevo_pago, dict):
        return jsonify({
            "mensaje": "Debe enviar los datos del pago"}), 400

    if (
        nuevo_pago.get("reserva_id") is None
        or not nuevo_pago.get("metodo_pago")
    ):
        return jsonify({"mensaje": "Faltan campos obligatorios"}), 400

    try:
        reserva_id = int(nuevo_pago["reserva_id"])

        if reserva_id <= 0:
            raise ValueError

    except (ValueError, TypeError):
        return jsonify({"mensaje": "ID de reserva inválido"}), 400

    reserva, error = consultar_reserva(reserva_id)

    if error:
        return error

    if reserva.get("estado") == "cancelada":
        return jsonify({"mensaje": "No se puede pagar una reserva cancelada"}), 409

    try:
        total = calcular_total(reserva)

    except (
        ValueError,
        KeyError,
        TypeError,
        InvalidOperation
    ):
        return jsonify({
            "mensaje": "No se pudo calcular el total de la reserva"
        }), 422

    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)

    sql = """
        INSERT INTO pagos
            (reserva_id, monto, metodo_pago, estado)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """

    valores = (
        reserva_id,
        total,
        nuevo_pago["metodo_pago"],
        "pendiente",
    )

    cursor.execute(sql, valores)

    nuevo_id = cursor.fetchone()["id"]

    conexion.commit()
    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Pago creado correctamente",
        "id": nuevo_id,
        "reserva_id": reserva_id,
        "monto": float(total),
        "estado": "pendiente"
    }), 201


crear_tabla()

app.run(host="0.0.0.0",port=5000,debug=True)
