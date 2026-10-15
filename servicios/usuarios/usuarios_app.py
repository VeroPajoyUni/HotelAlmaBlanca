import os
import requests
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
import psycopg
from usuarios_db import conectar, crear_tabla

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

@app.route("/usuarios", methods=["GET"])
def listarUsuarios():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(usuarios), 200


@app.route("/usuarios/<int:id>", methods=["GET"])
def buscarUsuario(id):
    conexion = conectar()
    cursor = conexion.cursor()
    sql = "SELECT * FROM usuarios WHERE id = %s"
    cursor.execute(sql, (id,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    if usuario is None:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    return jsonify(usuario), 200


@app.route("/usuarios", methods=["POST"])
def crearUsuario():
    nuevoUsuario = request.json

    conexion = conectar()
    cursor = conexion.cursor()

    sql = """
    INSERT INTO usuarios
    (nombre, apellido, documento, email, telefono)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
    """

    valores = (
        nuevoUsuario["nombre"],
        nuevoUsuario["apellido"],
        nuevoUsuario["documento"],
        nuevoUsuario["email"],
        nuevoUsuario["telefono"]
    )

    try:
        cursor.execute(sql, valores)
    except psycopg.errors.UniqueViolation:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Ya existe un usuario con ese documento o correo"}), 409
    idNuevo = cursor.fetchone()["id"]
    conexion.commit()

    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Usuario creado",
        "id": idNuevo
    }), 201


@app.route("/usuarios/<int:id>", methods=["PUT"])
def actualizarCompleto(id):
    editarUsuario = request.json
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE id = %s",
        (id,))
    usuario = cursor.fetchone()
    if usuario is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    sql = """
    UPDATE usuarios
    SET nombre = %s,
        apellido = %s,
        documento = %s,
        email = %s,
        telefono = %s
    WHERE id = %s
    """

    valores = (
        editarUsuario["nombre"],
        editarUsuario["apellido"],
        editarUsuario["documento"],
        editarUsuario["email"],
        editarUsuario["telefono"],
        id
    )
    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({
        "mensaje": "Usuario actualizado completamente"
    }), 200


@app.route("/usuarios/<int:id>", methods=["PATCH"])
def actualizarParcial(id):
    editarUsuario = request.json
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE id = %s",
        (id,)
    )
    usuario = cursor.fetchone()
    if usuario is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    nombre = editarUsuario.get("nombre", usuario["nombre"])
    apellido = editarUsuario.get("apellido", usuario["apellido"])
    documento = editarUsuario.get("documento", usuario["documento"])
    email = editarUsuario.get("email", usuario["email"])
    telefono = editarUsuario.get("telefono", usuario["telefono"])

    sql = """
    UPDATE usuarios
    SET nombre = %s,
        apellido = %s,
        documento = %s,
        email = %s,
        telefono = %s
    WHERE id = %s
    """

    valores = (
        nombre,
        apellido,
        documento,
        email,
        telefono,
        id
    )

    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Usuario actualizado parcialmente"
    }), 200


@app.route("/usuarios/<int:id>", methods=["DELETE"])
def eliminarUsuario(id):
    conexion = conectar()
    cursor = conexion.cursor()

    sql = "DELETE FROM usuarios WHERE id = %s"
    cursor.execute(sql, (id,))

    filasEliminadas = cursor.rowcount
    conexion.commit()

    cursor.close()
    conexion.close()

    if filasEliminadas == 0:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    return jsonify({
        "mensaje": "Usuario eliminado"
    }), 200

# Consulta de reservas de un usuario

@app.route("/usuarios/<int:id>/reservas", methods=["GET"])
def consultarReservasUsuario(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE id = %s",
        (id,)
    )
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    if usuario is None:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    reservasUrl = os.getenv("RESERVAS_URL", "http://localhost:5002")
    respuesta = requests.get(
        f"{reservasUrl.rstrip('/')}/reservas",
        params={"usuario_id": id},
        timeout=5
    )
    reservas = respuesta.json()
    return jsonify({
        "usuario": usuario,
        "reservas": reservas
    }), 200


# ---------- Arranque: crear la tabla si no existe y encender el servidor ----------
crear_tabla()
app.run(host="0.0.0.0", debug=True)
