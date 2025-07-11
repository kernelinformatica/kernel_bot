# chat-box-kernel/chat_router.py
import logging
import time

import requests
from flask import Blueprint, request, jsonify
from controller import obtener_saldos, buscarEmpresasAsociadas, buscarEmpresas, traerEmpresas, mercadoCereales, obtenerResumenDeCereales
from auth_router import login, generarToken, verificarTelefonoUsuario

chat_bp = Blueprint('chat', __name__)
usuarios_autenticados = {}
selecciones = {}


@chat_bp.route('/saldo', methods=['POST'])
def consultar_saldo():
    data = request.get_json()
    nro_celular = data.get('celular', 0)  # ejemplo: "3815432123"
    moneda = data.get('moneda', "PES")  # ejemplo por default: "PES"
    cuenta = data.get('cuenta', "0")
    if not nro_celular or not moneda:
        return jsonify({"error": "Faltan datos para consultar el saldo de cuenta corriente"}), 400

    usuarios = verificarTelefonoUsuario(nro_celular)




    if len(usuarios) > 1:

        empresas = buscarEmpresasAsociadas(nro_celular)

        return jsonify({"message": empresas})



    else:
        print("==========================================> "+ nro_celular, moneda, cuenta+ " <==========================================")
        return jsonify({"message":  obtener_saldos(nro_celular, moneda, cuenta)})





@chat_bp.route('/resumen-cereales', methods=['POST'])
def consultar_resumen_cereales():
    data = request.get_json()
    nro_celular = data.get('celular', 0)  # ejemplo: "3815432123"
    if not nro_celular :
        return jsonify({"Error": "Faltan datos para consultar el resumen de cereales"}), 400

    usuarios = verificarTelefonoUsuario(nro_celular)
    cuenta = "0"
    if len(usuarios) > 1:
        empresas = buscarEmpresasAsociadas(nro_celular)
        return jsonify({"message": empresas})
    else:
        for usuario in usuarios:
            cuenta = usuario['cuenta']
        return jsonify({"message":  obtenerResumenDeCereales(nro_celular, cuenta)})

@chat_bp.route('/mercado-cereales', methods=['POST'])
def consultar_mercado_cereales():
    data = request.get_json()
    nro_celular = data.get('celular', 0)
    tipo = data.get("tipo", "disponible")

    if not nro_celular :
        return jsonify({"Error": "Faltan datos para consultar el resumen de cereales"}), 400

    usuarios = verificarTelefonoUsuario(nro_celular)
    cuenta = "0"
    if len(usuarios) > 1:
        empresas = buscarEmpresasAsociadas(nro_celular)
        return jsonify({"message": empresas})
    else:
        for usuario in usuarios:
            cuenta = usuario['cuenta']
        return jsonify({"message":  mercadoCereales(nro_celular, cuenta, tipo)})


@chat_bp.route('/recibe-mensaje', methods=['POST'])
def recibir_mensaje():
    data = request.get_json()
    mensaje = data.get("message", "").lower()
    numero = data.get("phone")
    token = data.get("token", None)

    if numero not in usuarios_autenticados:
        if "usuario:" in mensaje and "clave:" in mensaje:
            partes = mensaje.split()
            usuario = partes[0].split(":")[1]
            clave = partes[1].split(":")[1]
            # Aquí deberías usar tu función de login real
            # user = login(usuario, clave)
            # Simulación:
            user = {"id": usuario, "nombre": usuario}  # Reemplaza por login real
            if user:
                usuarios_autenticados[numero] = user['id']
                return jsonify({"message": f"✅ Bienvenido {user['nombre']}. Escribí 'saldo' para consultar tu cuenta."})
            else:
                return jsonify({"message": "❌ Usuario o clave incorrectos."})
        else:
            return jsonify({"message": "🔐 Enviá tus credenciales así: usuario:TUNOMBRE clave:TUPASS"})
    else:
        if "saldo" in mensaje:
            return jsonify({"message": obtener_saldos(usuarios_autenticados[numero], token)})
        elif "cerrar sesión" in mensaje:
            usuarios_autenticados.pop(numero)
            return jsonify({"message": "🔒 Sesión cerrada. Hasta pronto."})
        else:
            return jsonify({"message": "🤖 Comando no reconocido. Escribí 'saldo' o 'cerrar sesión'."})

@chat_bp.route('/envia-mensaje', methods=['POST'])
def enviarMensajes():
    #POST / message / sendText / {instance}
    #Donde  {instance} es  el ID  de tu instancia activa(por ejemplo, la que está  conectada a WhatsApp).
    API_URL = "http://localhost:8080/message/sendText"
    API_KEY = "alberdi11"  # tu clave personalizada definida al iniciar Evolution API

    # Datos del mensaje
    data = {
        "phone": "5493416435556",  # Número destino (sin +, con código de país)
        "message": "¡Hola desde mi bot en Python! 🐍💬"
    }

    # Enviar POST
    response = requests.post(
        API_URL,
        headers={"Content-Type": "application/json", "apikey": API_KEY},
        json=data
    )

    # Mostrar respuesta
    print("Status code:", response.status_code)
    print("Respuesta JSON:", response.json())



def traerInstancias():
    #GET / instance / list
    #Donde  {instance} es  el ID  de tu instancia activa(por ejemplo, la que está  conectada a WhatsApp).
    API_KEY = "Respuesta: {'status': 401, 'error': 'Unauthorized', 'response': {'message': 'Unauthorized'}}"  # tu clave personalizada definida al iniciar Evolution API
    url = "http://localhost:8080/instance/fetchInstances"

    headers = {
        "apikey": API_KEY  # Reemplazalo con tu API key real si es necesario
    }

    response = requests.get(url, headers=headers)

    print("Código de estado:", response.status_code)
    print("Respuesta:", response.json())







@chat_bp.route('/set-empresa', methods=['POST'])
def setEmpresa():
    data = request.get_json()
    celular = data.get('celular')
    cooperativa = data.get('cooperativa')
    if not celular or not cooperativa:
        return jsonify({"error": "Faltan datos para establecer la cooperativa"}), 400

    # Almacena la selección con un tiempo de expiración
    selecciones[celular] = {
        "cooperativa": cooperativa,
        "expiracion": time.time() + 3600  # 1 hora en segundos
    }

    return jsonify({"message": f"Cooperativa {cooperativa} seleccionada para el celular {celular}."})


@chat_bp.route('/get-empresas', methods=['POST'])
def traerEmpresasAsociadas():
    data = request.get_json()
    celular =  data.get('celular')
    coope = data.get('coope', 0)
    print("CELULAR:", celular)

    if not celular:
        return jsonify({"error": "Falta el  CELULAR."}), 400

    empresas = traerEmpresas(celular, coope)

    if empresas is None:
        return jsonify({"error": "Código inválido"}), 404


    return empresas









@chat_bp.route('/get-empresa', methods=['POST'])
def getEmpresa():
    data = request.get_json()
    celular = data.get('celular')
    coope = data.get('coope')

    if not coope:
        return jsonify({"error": "Falta el  codigo de empresa"}), 400

    empresa = buscarEmpresas(celular, coope)

    if empresa is None:
        return jsonify({"error": "Código inválido"}), 404

    return jsonify({"message": empresa})






@chat_bp.route('/dummy', methods=['GET'])
def dummy():
    import json
    data = {
        "code": "1",
        "version": "1.0",
        "status": 200,
        "description": "ChatBox Kernel informática, hola soy el chatbox kernel, y funciono correctamente. ¿En que te puedo ayudar hoy?",
        "name": "Conciliaciones",
        "message": "ChatBox Kernel informática, hola soy el chatbox kernel, y funciono correctamente. ¿En que te puedo ayudar hoy?",
        "functions": ["login", "dummy", "logout"]
    }
    json_output = json.dumps(data, indent=4)
    logging.info(json_output)
    return json_output


@chat_bp.route('/tester', methods=['GET'])
def prueba():
    nro_celular = "5493412178626"
    empresas = buscarEmpresasAsociadas(nro_celular)

    return jsonify({"message": empresas})
