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



app.run(host="0.0.0.0", port=5000)