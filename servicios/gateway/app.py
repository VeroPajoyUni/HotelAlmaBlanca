from flask import Flask, jsonify, request, Response
import os
import requests

app = Flask(__name__)

USUARIOS_URL = os.getenv("USUARIOS_URL", "http://usuarios:5000")
HABITACIONES_URL = os.getenv("HABITACIONES_URL", "http://habitaciones:5000")
RESERVAS_URL = os.getenv("RESERVAS_URL", "http://reservas:5000")
PAGOS_URL = os.getenv("PAGOS_URL", "http://pagos:5000")
NOTIFICACIONES_URL = os.getenv("NOTIFICACIONES_URL", "http://notificaciones:5000")

def reenviar(metodo, url):
    try:
        respuesta = requests.request(
            metodo,
            url,
            params=request.args,
            json=request.get_json(silent=True),
            timeout=5
        )
        return Response(
            respuesta.content,
            status=respuesta.status_code,
            content_type=respuesta.headers.get("Content-Type", "application/json")
        )
    except requests.exceptions.Timeout:
        return jsonify({
            "mensaje": "El servicio tardó mucho en responder"
        }), 504
    except requests.exceptions.ConnectionError:
        return jsonify({
            "mensaje": "El servicio no está disponible"
        }), 503

@app.route("/usuarios", methods=["GET", "POST"])
def ruta_usuarios():
    return reenviar(request.method, USUARIOS_URL + "/usuarios")

@app.route("/usuarios/<int:id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def ruta_usuarios_detalle(id):
    return reenviar(request.method, USUARIOS_URL + "/usuarios/" + str(id))

@app.route("/habitaciones", methods=["GET", "POST"])
def ruta_habitaciones():
    return reenviar(request.method, HABITACIONES_URL + "/habitaciones")


@app.route("/habitaciones/<int:id>", methods=["GET", "PUT", "DELETE"])
def ruta_habitaciones_detalle(id):
    return reenviar(request.method, HABITACIONES_URL + "/habitaciones/" + str(id))


@app.route("/reservas", methods=["GET", "POST"])
def ruta_reservas():
    return reenviar(request.method, RESERVAS_URL + "/reservas")


@app.route("/reservas/disponibilidad", methods=["GET"])
def ruta_reservas_disponibilidad():
    return reenviar(request.method, RESERVAS_URL + "/reservas/disponibilidad")


@app.route("/reservas/<int:id>", methods=["GET", "PUT", "DELETE"])
def ruta_reservas_detalle(id):
    return reenviar(request.method, RESERVAS_URL + "/reservas/" + str(id))


@app.route("/reservas/<int:id>/detalles", methods=["GET"])
def ruta_reservas_detalles(id):
    return reenviar(request.method, RESERVAS_URL + "/reservas/" + str(id) + "/detalles")


@app.route("/pagos", methods=["GET", "POST"])
def ruta_pagos():
    return reenviar(request.method, PAGOS_URL + "/pagos")


@app.route("/pagos/<int:id>", methods=["GET"])
def ruta_pagos_detalle(id):
    return reenviar(request.method, PAGOS_URL + "/pagos/" + str(id))


@app.route("/notificaciones", methods=["GET", "POST"])
def ruta_notificaciones():
    return reenviar(request.method, NOTIFICACIONES_URL + "/notificaciones")

app.run(host="0.0.0.0", port=5000)