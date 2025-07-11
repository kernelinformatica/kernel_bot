import configparser
import os
import sys

import mysql.connector
from mysql.connector import Error

class GestAgroConnection:
    def __init__(self):

        config = configparser.ConfigParser()
        config_file = "config.ini"
        if getattr(sys, 'frozen', False):
            # Usar sys._MEIPASS cuando esté empaquetado
            base_path = sys._MEIPASS
        else:
            # Usar el directorio del archivo cuando esté ejecutándose como script
            base_path = os.path.dirname(__file__)

        config_file = os.path.join(base_path, config_file)
        config = configparser.ConfigParser()

        if not os.path.exists(config_file):
            #print(":: El archivo de configuración no existe, se define la configuración por defecto en modo produccion 'gestagro_consulta' ::")
            self.host = "149.50.144.239"
            self.database = "gestagro_consulta"
            self.user = "vps4_root"
            self.password = "Humb3rt01"
            self.port = "3306"
            self.conn = self.create_connection()
        else:
            config.read(config_file)
            self.host = config['CONEXION_GESTAGRO']['host']
            self.database = config['CONEXION_GESTAGRO']['database']
            self.user = config['CONEXION_GESTAGRO']['user']
            self.password = config['CONEXION_GESTAGRO']['password']
            self.port = config['CONEXION_GESTAGRO']['port']
            self.conn = self.create_connection()
            #print("Conectando a la base de datos desde el archivo de configuracion-> " + str(self.host) + " | " + str(self.database))

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
                #print("Connection to MySQL se ha establecido con éxito.")
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

