
import logging
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from auth_router import auth_bp, dummy, login
from chat_router import chat_bp, enviarMensajes, traerInstancias
from conn.GestAgroConnection import GestAgroConnection as GestAgroConnection
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
app = Flask(__name__)


class AppChatBox(GestAgroConnection):
        def __init__(self):
            super().__init__()
            self.app = Flask(__name__)
            CORS(self.app)

            self.app.register_blueprint(auth_bp, url_prefix='/api/auth')
            self.app.register_blueprint(chat_bp, url_prefix='/api/chat')
        def run(self, debug=True, host="0.0.0.0", port=5070):
            self.app.run(debug=True, host=host, port=port)


    # **🚀 Ejecutar el servidor Flask**

if __name__ == "__main__":
     chatBox = AppChatBox()
     try:
       with chatBox.app.app_context():
             chatBox.run(debug=True, port=5070)

     except Exception as e:
       logging.error(f"Error al iniciar el servicio: {e}")

"""
if __name__ == "__main__":
    chatbox = AppChatBox()
    try:
        with chatbox.app.test_request_context():
            try:

                # Simulación de un token, deberías obtenerlo de tu sistema de autenticación real
                token = "$2b$10$2wTqVeOsDBPcgOi.XuwzJ.KOB80.fb./JJIsvuYE/z/SZOs64gjMG"

                #solicito saldo, suponiendo que el token es válido y que ya se logueo previantemente desde el whats up
                #saldo = obtener_saldo("1100302", "PES", token)
                #logging.info(f"Saldo obtenido: {saldo}")

                #login
                #login = login("1100302", "dario")
                #logging.info(login)

                #ENVIA MENSAJE
                mensaje = traerInstancias()
                logging.info(f"traerInstancias : {mensaje}")

            except Exception as e:
                logging.error(f"Error al ejecutar el metodo: {e}")
    except Exception as e:
        logging.error(f"Error general: {e}")
"""