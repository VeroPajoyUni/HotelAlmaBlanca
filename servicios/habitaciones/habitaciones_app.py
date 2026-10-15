from flask import Flask, jsonify, request
from psycopg.rows import dict_row
from werkzeug.exceptions import HTTPException
from habitaciones_db import conectar, crear_tabla

app = Flask(__name__)

# ---------- CORS: permite que la página Home (otro puerto) consuma esta API ----------
@app.after_request
def permitir_cors(respuesta):
    respuesta.headers["Access-Control-Allow-Origin"] = "*"
    respuesta.headers["Access-Control-Allow-Headers"] = "Content-Type"
    respuesta.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE"
    return respuesta

# ---------- Errores inesperados: responder en JSON para que el navegador pueda leerlos ----------
@app.errorhandler(Exception)
def error_interno(error):
    if isinstance(error, HTTPException):
        return error
    app.logger.exception("Error inesperado")
    return jsonify({"mensaje": f"Error interno del servicio: {error}"}), 500
app.json.ensure_ascii = False

@app.route("/health")
def health():
    return jsonify({"servicio": "habitaciones", "estado": "ok"})

@app.route("/habitaciones")
def listar():
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    sql = "SELECT * FROM habitaciones ORDER BY id"
    cursor.execute(sql)
    habitaciones = cursor.fetchall()
    cursor.close()
    conexion.close()

    for habitacion in habitaciones:
        habitacion["precio_noche"] = float(habitacion["precio_noche"])

    return jsonify(habitaciones)

@app.route("/habitaciones/<int:id>")
def buscar(id):
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    sql = """
        SELECT * FROM habitaciones WHERE id = %s
    """
    cursor.execute(sql, (id,))
    habitacion = cursor.fetchone()
    cursor.close()
    conexion.close()

    if habitacion is None:
        return jsonify({"mensaje": "Habitación no encontrada"}), 404

    habitacion["precio_noche"] = float(habitacion["precio_noche"])
    return jsonify(habitacion)

@app.route("/habitaciones", methods=["POST"])
def crear():
    nuevaHabitacion = request.json
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    sql = """
        INSERT INTO habitaciones
            (numero, tipo, capacidad, precio_noche, estado, descripcion)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    valores = (
        nuevaHabitacion["numero"],
        nuevaHabitacion["tipo"],
        nuevaHabitacion["capacidad"],
        nuevaHabitacion["precio_noche"],
        nuevaHabitacion["estado"],
        nuevaHabitacion.get("descripcion"),
    )
    cursor.execute(sql, valores)
    nuevoId = cursor.fetchone()["id"]
    conexion.commit()
    cursor.close()
    conexion.close()

    return jsonify({"mensaje": "Habitación creada correctamente", "id": nuevoId}), 201

@app.route("/habitaciones/<int:id>", methods=["PUT"])
def actualizar(id):
    editarHabitacion = request.json
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    sql = """
        UPDATE habitaciones
        SET numero = %s, tipo = %s, capacidad = %s, precio_noche = %s,
            estado = %s, descripcion = %s
        WHERE id = %s
        RETURNING id
    """
    valores = (
        editarHabitacion["numero"],
        editarHabitacion["tipo"],
        editarHabitacion["capacidad"],
        editarHabitacion["precio_noche"],
        editarHabitacion["estado"],
        editarHabitacion.get("descripcion"),
        id,
    )
    cursor.execute(sql, valores)
    habitacion = cursor.fetchone()
    conexion.commit()
    cursor.close()
    conexion.close()

    if habitacion is None:
        return jsonify({"mensaje": "Habitación no encontrada"}), 404

    return jsonify({"mensaje": "Habitación actualizada correctamente"})

@app.route("/habitaciones/<int:id>", methods=["DELETE"])
def eliminar(id):
    conexion = conectar()
    cursor = conexion.cursor(row_factory=dict_row)
    sql = """
        DELETE FROM habitaciones
        WHERE id = %s
        RETURNING id
    """
    cursor.execute(sql, (id,))
    habitacion = cursor.fetchone()
    conexion.commit()
    cursor.close()
    conexion.close()

    if habitacion is None:
        return jsonify({"mensaje": "Habitación no encontrada"}), 404

    return jsonify({"mensaje": "Habitación eliminada correctamente"})


# ---------- Arranque: crear la tabla si no existe y encender el servidor ----------
crear_tabla()
app.run(host="0.0.0.0", port=5000, debug=True)
