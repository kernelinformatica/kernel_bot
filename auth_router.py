from datetime import datetime, timedelta
import bcrypt
import hashlib
from flask import Blueprint, request, jsonify, Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from conn.GestAgroConnection import GestAgroConnection as GestAgroConnection
import logging
load_dotenv()

auth_bp = Blueprint('/auth', __name__)
app = Flask(__name__)
app.config['DEBUG'] = True
load_dotenv()
API_NOMBRE = os.getenv('API_NOMBRE')
CORS(app)

@auth_bp.route('/login', methods=['POST'])
def login(usuario, clave):
    conn = GestAgroConnection().conn
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE cuenta = %s", (usuario,))
    user = cursor.fetchone()
    conn.close()
    if user:
        clave_md5 = hashlib.md5(clave.encode()).hexdigest()
        if clave_md5 == user['clave']:
            # me tengo que fijar si hay token vigente si no tengo que generar uno nuevo
            conn = GestAgroConnection().conn
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as cantidad FROM userTokens  WHERE username = %s AND dateTo >= NOW()", (usuario,))
            resu = cursor.fetchone()
            conn.close()
            token_existe = resu['cantidad']
            if token_existe > 0:
                conn = GestAgroConnection().conn
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT hashId FROM userTokens  WHERE username = %s AND dateTo >= NOW()", (usuario,))
                token_resu = cursor.fetchone()
                conn.close()
                token = token_resu["hashId"]
            else:
                token_nuevo = generarToken(usuario)
                token = token_nuevo["hashId"]
            data = {
                "code": "OK",
                "status": 200,
                "description": "Autentificación existosa.",
                "name": API_NOMBRE,
                "message": "Autentificación existosa.",
                "token" : str(token)
            }
            return data
    data = {
        "code": "ERROR",
        "status": 200,
        "description": "Usuario o clave incorrectos.",
        "name": API_NOMBRE,
        "message": "Usuario o clave incorrectos.",
        "token": ""

    }
    return data
def verificarToken(usuario, token):
    conn = GestAgroConnection().conn
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM userTokens  WHERE hashId = %s and username = %s AND dateTo >= NOW()", (token, usuario))
    token_resu = cursor.fetchone()
    conn.close()
    if token_resu is not None:
        return True
    else:
        return False
def generarToken(usuario):
    now = datetime.now().strftime("%Y%m%d%H%M%S")  # ej. '20250627123845'
    salt = bcrypt.gensalt(rounds=10)
    token_bcrypt = bcrypt.hashpw(now.encode(), salt)

    conn = GestAgroConnection().conn
    cursor = conn.cursor(dictionary=True)
    fecha_vencimiento = datetime.now() + timedelta(days=1)  # por ejemplo, 24hs desde ahora
    coope = usuario[:2]
    fecha_actual = datetime.now()
    origen = "chatbox"
    # Insertar nuevo token
    cursor.execute(
        "INSERT INTO userTokens (hashId, coope, username, dateFrom, dateTo, source) VALUES (%s, %s, %s, %s, %s, %s)",
        (token_bcrypt, coope, usuario, fecha_actual, fecha_vencimiento, origen)
    )
    conn.commit()
    conn = GestAgroConnection().conn
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM userTokens  WHERE hashId = %s", (token_bcrypt,))
    token_resu = cursor.fetchone()
    conn.close()
    token = token_resu
    return token
def verificarTelefonoUsuario(nroCelular):
    conn = GestAgroConnection().conn
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE telefono = %s", (nroCelular,))
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios


@auth_bp.route('/dummy', methods=['GET'])
def dummy():
    import json
    data = {
        "code": "1",
        "version": "1.0",
        "status": 200,
        "description": API_NOMBRE+", servicio de autentificación funciona correctamente.",
        "name": API_NOMBRE,
        "message": API_NOMBRE+" servicio de autentificación funciona correctamente.",
        "functions": ["login", "dummy", "logout"]
    }
    json_output = json.dumps(data, indent=4)
    logging.info(json_output)
    return json_output