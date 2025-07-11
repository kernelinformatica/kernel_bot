import configparser
import os
import sys

import mysql.connector
from mysql.connector import Error

class WebConnection:
    def __init__(self):
        config_file = r"H:\Dario\Proyectos\Python\kernel\ws-rest\chat_bot_kernel\config.ini"

        if getattr(sys, 'frozen', False):
            # Usar sys._MEIPASS cuando esté empaquetado
            base_path = sys._MEIPASS
        else:
            # Usar el directorio del archivo cuando esté ejecutándose como script
            base_path = os.path.dirname(__file__)

        config_file = os.path.join(base_path, config_file)
        config = configparser.ConfigParser()
        print(config_file)
        config.read(config_file)
        if not os.path.exists(config_file):
            self.host = "192.168.254.47"
            self.database = "c4_kernel_coops_db"
            self.user = "c4_root"
            self.password = "kernelAlberdi11"
            self.port = "3306"

            print(
                ":: WEB CONNECTION: El archivo de configuración no existe, se define la configuración por defecto en modo produccion 'c4_kernel_coops_db'  :: " + str(self.host) + " | " + str(self.database) + " | " + str(self.user) + " | " + str(self.password) + " | " + str(self.port))

        else:
            print(":::::: WEB CONNECTION: Leyendo el archivo de configuración -> " + str( config['CONEXION_WEB']['host']) + " ::::::")
            self.host = config['CONEXION_WEB']['host']
            self.database = config['CONEXION_WEB']['database']
            self.user = config['CONEXION_WEB']['user']
            self.password = config['CONEXION_WEB']['password']
            self.port = config['CONEXION_WEB']['port']
        self.conn = self.create_connection()

    def create_connection(self):
        try:
            conn = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port = self.port
            )
            print("Conectando a la base de datos -> " + str(self.host) + " | " + str(self.database) + " | " + str(self.user) + " | " + str(self.password) + " | " + str(self.port))
            if conn.is_connected():
                return conn
        except Error as e:
            print(f"Error: {e}")
            self.conn = None

    def execute(self, query):
        if self.conn is None:
            print("La Connection no se pudo establecer")
            return None
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            self.conn.commit()

        except Error as e:
            print(f"Error: {e}")
            return None
        return cursor
    def executemany(self, query, rows):

        if self.conn is None:
            print("La Connection no se pudo establecer")
            return None
        cursor = self.conn.cursor()
        try:
            cursor.executemany(query, rows)
            self.conn.commit()
            print(f'{cursor.rowcount} registros insertados con éxito')
        except Error as e:
            print(f"Error: {e}")
            return None
        return cursor
    def close_connection(self):
        if self.conn is not None and self.conn.is_connected():
            self.conn.close()
            print("Connection cerrada")

