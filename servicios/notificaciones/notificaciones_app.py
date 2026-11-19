from flask import Flask, jsonify, request
from psycopg.rows import dict_row

from notificaciones_db import conectar, crear_tabla


app = Flask(__name__)
app.json.ensure_ascii = False

ESTADOS = {"pendiente", "leida"}
CAMPOS_EDITABLES = {"usuario_id", "tipo", "mensaje", "estado"}

def validar_datos(datos, parcial=False):
    if not isinstance(datos, dict):
        return None, "Debe enviar los datos de la notificación en formato JSON"

    if set(datos) - CAMPOS_EDITABLES:
        return None, "La solicitud contiene campos no permitidos"

    if not datos:
        return None, "Debe enviar al menos un campo para actualizar"

    if not parcial and {"usuario_id", "tipo", "mensaje"} - set(datos):
        return None, "Faltan campos obligatorios: usuario_id, tipo y mensaje"

    resultado = {}
    if "usuario_id" in datos:
        usuario_id = datos["usuario_id"]
        if (
            isinstance(usuario_id, bool)
            or not isinstance(usuario_id, int)
            or usuario_id <= 0
        ):
            return None, "usuario_id debe ser un entero positivo"
        resultado["usuario_id"] = usuario_id

    for campo in ("tipo", "mensaje"):
        if campo in datos:
            valor = datos[campo]
            if not isinstance(valor, str) or not valor.strip():
                return None, f"{campo} debe ser un texto no vacío"
            resultado[campo] = valor.strip()

    if "estado" in datos:
        estado = datos["estado"]
        if not isinstance(estado, str) or estado not in ESTADOS:
            return None, "estado debe ser 'pendiente' o 'leida'"
        resultado["estado"] = estado
    elif not parcial:
        resultado["estado"] = "pendiente"

    return resultado, None


@app.after_request
def permitir_cors(respuesta):
    respuesta.headers["Access-Control-Allow-Origin"] = "*"
    respuesta.headers["Access-Control-Allow-Headers"] = "Content-Type"
    respuesta.headers["Access-Control-Allow-Methods"] = (
        "GET, POST, PUT, PATCH, DELETE"
    )
    return respuesta


@app.route("/notificaciones", methods=["GET"])
def listar():
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    cursor.execute("SELECT * FROM notificaciones ORDER BY id")
    notificaciones = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(notificaciones), 200


@app.route("/notificaciones/<int:id_notificacion>", methods=["GET"])
def buscar(id_notificacion):
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    cursor.execute(
        "SELECT * FROM notificaciones WHERE id = %s",
        (id_notificacion,),
    )
    notificacion = cursor.fetchone()
    cursor.close()
    conexion.close()

    if notificacion is None:
        return jsonify({"mensaje": "Notificación no encontrada"}), 404
    return jsonify(notificacion), 200


@app.route("/notificaciones", methods=["POST"])
def crear():
    datos, error = validar_datos(request.get_json(silent=True))
    if error:
        return jsonify({"mensaje": error}), 400

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO notificaciones (usuario_id, tipo, mensaje, estado)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (
            datos["usuario_id"],
            datos["tipo"],
            datos["mensaje"],
            datos["estado"],
        ),
    )
    id_notificacion = cursor.fetchone()[0]
    conexion.commit()
    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Notificación creada correctamente",
        "id": id_notificacion,
    }), 201


def actualizar_notificacion(id_notificacion, cambios, reemplazar=False):
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    cursor.execute(
        "SELECT * FROM notificaciones WHERE id = %s",
        (id_notificacion,),
    )
    notificacion = cursor.fetchone()
    if notificacion is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Notificación no encontrada"}), 404

    if reemplazar:
        usuario_id = cambios["usuario_id"]
        tipo = cambios["tipo"]
        mensaje = cambios["mensaje"]
        estado = cambios.get("estado", "pendiente")
    else:
        usuario_id = cambios.get("usuario_id", notificacion["usuario_id"])
        tipo = cambios.get("tipo", notificacion["tipo"])
        mensaje = cambios.get("mensaje", notificacion["mensaje"])
        estado = cambios.get("estado", notificacion["estado"])

    cursor.execute(
        """
        UPDATE notificaciones
        SET usuario_id = %s, tipo = %s, mensaje = %s, estado = %s,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = %s
        """,
        (usuario_id, tipo, mensaje, estado, id_notificacion),
    )
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Notificación actualizada correctamente"}), 200


@app.route("/notificaciones/<int:id_notificacion>", methods=["PUT"])
def reemplazar(id_notificacion):
    datos, error = validar_datos(request.get_json(silent=True))
    if error:
        return jsonify({"mensaje": error}), 400
    return actualizar_notificacion(id_notificacion, datos, reemplazar=True)


@app.route("/notificaciones/<int:id_notificacion>", methods=["PATCH"])
def actualizar(id_notificacion):
    datos, error = validar_datos(
        request.get_json(silent=True), parcial=True
    )
    if error:
        return jsonify({"mensaje": error}), 400
    return actualizar_notificacion(id_notificacion, datos)


@app.route("/notificaciones/<int:id_notificacion>", methods=["DELETE"])
def eliminar(id_notificacion):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "DELETE FROM notificaciones WHERE id = %s",
        (id_notificacion,),
    )
    eliminadas = cursor.rowcount
    conexion.commit()
    cursor.close()
    conexion.close()

    if eliminadas == 0:
        return jsonify({"mensaje": "Notificación no encontrada"}), 404
    return "", 204


crear_tabla()
app.run(host="0.0.0.0", port=5000, debug=True)
