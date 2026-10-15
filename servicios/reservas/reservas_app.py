import os

from flask import Flask, jsonify, request
import requests
from psycopg.rows import dict_row
from reservas_db import conectar

habitaciones_url = os.getenv("HABITACIONES_URL")
usuarios_url = os.getenv("USUARIOS_URL")

app = Flask(__name__)

def consultar_servicio(url, recurso, id):
    respuesta = requests.get(
        f"{url.rstrip('/')}/{recurso}/{id}",
        timeout=5
    )
    if respuesta.status_code == 404:
        mensaje = "Usuario no encontrado" if recurso == "usuarios" else "Habitación no encontrada"
        return None, (jsonify({"mensaje": mensaje}), 404)
    if respuesta.status_code != 200:
        return None, (jsonify({"mensaje": f"Error al consultar el servicio de {recurso}"}), 503)
    return respuesta.json(), None

def habitacion_disponible(cursor, habitacion_id, fecha_entrada, fecha_salida, reserva_id=None):
    sql = """
        SELECT id FROM reservas
        WHERE habitacion_id = %s
          AND estado <> 'cancelada'
          AND fecha_entrada < %s
          AND fecha_salida > %s
    """
    valores = [habitacion_id, fecha_salida, fecha_entrada]

    if reserva_id is not None:
        sql += " AND id <> %s"
        valores.append(reserva_id)

    cursor.execute(sql, tuple(valores))
    return cursor.fetchone() is None

@app.route("/reservas")
def listar():
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    sql = "SELECT * FROM reservas ORDER BY id"
    cursor.execute(sql)
    reservas = cursor.fetchall()
    cursor.close()
    conexion.close()

    return jsonify(reservas)

@app.route("/reservas/<int:id>")
def buscar(id):
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    sql = """
        SELECT * FROM reservas
        WHERE id = %s
    """
    cursor.execute(sql, (id,))
    reserva = cursor.fetchone()
    cursor.close()
    conexion.close()

    if reserva is None:
        return jsonify({"mensaje": "Reserva no encontrada"}), 404

    return jsonify(reserva)

@app.route("/reservas/<int:id>/detalles")
def detalles(id):
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    sql = """
        SELECT * FROM reservas
        WHERE id = %s
    """
    cursor.execute(sql, (id,))
    reserva = cursor.fetchone()
    cursor.close()
    conexion.close()

    if reserva is None:
        return jsonify({"mensaje": "Reserva no encontrada"}), 404

    usuario, error = consultar_servicio(
        usuarios_url, "usuarios", reserva["usuario_id"]
    )
    if error:
        return error
    habitacion, error = consultar_servicio(
        habitaciones_url, "habitaciones", reserva["habitacion_id"]
    )
    if error:
        return error

    reserva["usuario"] = usuario
    reserva["habitacion"] = habitacion
    return jsonify(reserva)


@app.route("/reservas/disponibilidad")
def consultar_disponibilidad():
    habitacion_id = request.args.get("habitacion_id")
    fecha_entrada = request.args.get("fecha_entrada")
    fecha_salida = request.args.get("fecha_salida")
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    disponible = habitacion_disponible(
        cursor, habitacion_id, fecha_entrada, fecha_salida
    )
    cursor.close()
    conexion.close()

    return jsonify({"disponible": disponible})

@app.route("/reservas", methods=["POST"])
def crear():
    nueva_reserva = request.json

    _, error = consultar_servicio(
        usuarios_url, "usuarios", nueva_reserva["usuario_id"]
    )
    if error:
        return error
    _, error = consultar_servicio(
        habitaciones_url, "habitaciones", nueva_reserva["habitacion_id"]
    )
    if error:
        return error

    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    if not habitacion_disponible(
        cursor,
        nueva_reserva["habitacion_id"],
        nueva_reserva["fecha_entrada"],
        nueva_reserva["fecha_salida"],
    ):
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "La habitación no está disponible"}), 409

    sql = """
        INSERT INTO reservas
            (usuario_id, habitacion_id, fecha_entrada, fecha_salida, huespedes)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    valores = (
        nueva_reserva["usuario_id"],
        nueva_reserva["habitacion_id"],
        nueva_reserva["fecha_entrada"],
        nueva_reserva["fecha_salida"],
        nueva_reserva["huespedes"],
    )
    cursor.execute(sql, valores)
    nuevoId = cursor.fetchone()["id"]
    conexion.commit()
    cursor.close()
    conexion.close()

    return jsonify({"mensaje": "Reserva creada correctamente", "id": nuevoId}), 201

@app.route("/reservas/<int:id>", methods=["DELETE"])
def eliminar(id):
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    sql = """
        DELETE FROM reservas WHERE id = %s
    """
    cursor.execute(sql, (id,))
    conexion.commit()
    cursor.close()
    conexion.close()

    return jsonify({"mensaje": "Reserva eliminada correctamente"})

@app.route("/reservas/<int:id>", methods=["PUT"])
def actualizar(id):
    datos = request.json
    _, error = consultar_servicio(
        usuarios_url, "usuarios", datos["usuario_id"]
    )
    if error:
        return error
    _, error = consultar_servicio(
        habitaciones_url, "habitaciones", datos["habitacion_id"]
    )
    if error:
        return error

    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    if not habitacion_disponible(
        cursor, datos["habitacion_id"], datos["fecha_entrada"], datos["fecha_salida"], id
    ):
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "La habitación no está disponible"}), 409

    sql = """
        UPDATE reservas
        SET usuario_id = %s, habitacion_id = %s, fecha_entrada = %s,
            fecha_salida = %s, huespedes = %s
        WHERE id = %s
    """
    valores = (
        datos["usuario_id"],
        datos["habitacion_id"],
        datos["fecha_entrada"],
        datos["fecha_salida"],
        datos["huespedes"],
        id,
    )
    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()
    conexion.close()

    return jsonify({"mensaje": "Reserva actualizada correctamente"})

app.run(host="0.0.0.0", port=5000, debug=True)
