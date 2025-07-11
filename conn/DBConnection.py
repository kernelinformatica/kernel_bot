import os

import pyodbc
import configparser
import logging
class DBConnection:
    def __init__(self):
        try:
            self.conn = self.create_connection()
        except pyodbc.Error as e:
            print("Error al conectar a la base de datos:", e)
            logging.error("Error al conectar a la base de datos: %s", e)
            self.conn = None
        except configparser.Error as e:
            print("Error al leer el archivo de configuración:", e)
            self.conn = None

    def create_connection(self):
        config = configparser.ConfigParser()
        config_file = 'config.ini'
        if not os.path.exists(config_file):
            logging.error("El archivo de configuración  no existe, se define valores locales", config_file)
            print(":: El archivo de configuración  no existe, se define valores locales ::")
            self.serv = "coope17"
            self.usr = "dba"
            self.passwd = "sql"
            self.db = "coope.db"
            self.prt = ""
            self.nombreCliente = "GestAgro"
            self.token ="8f3e69cb8fcebe9b61438ed56b84c3764f9c143e3fb3d223f842b56d27320c47"
        else:
            logging.info("Leyendo archivo de configuración ", config_file)
            print(":: Leyendo archivo de configuración  ::")
            config.read(config_file)
            self.serv = config['CONEXION']['serv']
            self.usr = config['CONEXION']['usr']
            self.passwd = config['CONEXION']['passwd']
            self.db = config['CONEXION']['db']
            self.prt = config['CONEXION']['prt']
            self.nombreCliente = config['EMPRESA']['nombre']
            self.token = config['TOKEN']['TOKEN']
            print("Conectando a la base de datos -> "+str(self.serv)+" | "+str(self.usr)+" | "+str(self.passwd)+" | "+str(self.db)+" | "+str(self.prt)+" | "+str(self.nombreCliente)+" | "  +str(self.token))

        conn = pyodbc.connect('DSN=' + self.serv + ';Database=' + self.db + ';UID=' + self.usr + ';PWD=' + self.passwd,
                              autocommit=True)
        conn.setdecoding(pyodbc.SQL_CHAR, encoding='latin1')
        conn.setencoding('latin1')
        return conn