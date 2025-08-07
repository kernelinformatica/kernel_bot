import os
from datetime import datetime, timedelta


from flask import jsonify, logging

from utils.emoji_lib import get_emoji
from datetime import datetime
from conn.GestAgroConnection import GestAgroConnection as GestAgroConnection
from conn.WebConnection import WebConnection as WebConnection
from  auth_router import verificarToken
from dotenv import load_dotenv

load_dotenv()
API_NOMBRE = os.getenv('API_NOMBRE', 'GestAgroBot')
msg_info = f"Bienvenido a {API_NOMBRE}, el bot de asistencia para usuarios de GestAgro. Aquí podrás consultar tu saldo, resumen de cereales y mercados de cereales de tu cooperativa. Para comenzar, por favor autentifícate enviando tu número de celular o cuenta."
msg_menu = f"\n\n🤖 Escribi *menu* para volver al menu principal. "
msg_instrucciones = f"\nPara descargar en formato PDF la ficha de cereal clase y cosecha que desee debe enviar: *comando + cereal  + clase + cosecha.*\n\nPor ejemplo: *5 soja 0 2425*.\n\n*Si no sabe el código de *clase*, es el que aparece al lado del nombre del cereal (Cod:000).*\n\n"


def obtener_saldos(nroCelular, moneda="PES", cuenta="0"):
    if str(cuenta) == "0" or str(cuenta) == "" :
        usuario = traerUsuario(0, nroCelular)

    else:
        usuario = traerUsuario(cuenta, 0)

    nombre = usuario[3] if usuario else ""
    print("OBTENER SALDOS: ", nroCelular, moneda, cuenta, nombre)
    coope = usuario[0]
    empresa = traerEmpresa(coope)
    nombre_empresa = empresa[5] if empresa else "Empresa no encontrada"
    conn = GestAgroConnection().conn
    cursor = conn.cursor()
    if str(moneda) == "PES":
        # si cuenta es mayor a 0, se busca por cuenta
        if str(cuenta) != "0":
            cursor.execute("SELECT saldo, saldoGral, saldoDif, ultActualizacion,  cuenta, nombre, coope FROM usuarios WHERE cuenta = %s", (cuenta,))
        else:
            cursor.execute("SELECT saldo, saldoGral, saldoDif, ultActualizacion,  cuenta, nombre, coope FROM usuarios WHERE telefono = %s", (nroCelular,))
    elif str(moneda) == "USD":
        if str(cuenta) != "0":
            cursor.execute("SELECT saldoDolar AS saldo, saldoGralDolar as general, saldoDifDolar as diferido, ultActualizacion, cuenta, nombre, coope FROM usuarios WHERE cuenta = %s", (cuenta,))
        else:
            cursor.execute("SELECT saldoDolar AS saldo, saldoGralDolar as general, saldoDifDolar as diferido, ultActualizacion, cuenta, nombre, coope FROM usuarios WHERE telefono = %s", (nroCelular,))
    else:
        conn.close()
        return f"emojis('estado', 'error') No se pudo enviar el saldo, debido a un error temporal, inténte nuevamente más tarde."
    resultado = cursor.fetchone()
    if moneda == "PES":
        mon = "$"
        mon_nombre = "Pesos"
    elif moneda == "USD":
        mon = "USD"
        mon_nombre = "Dólares"

    respuesta = (
        f"*{resultado[5]}.*\n"
        f"Cuenta: *{resultado[4]}*\n\n"
        f"💰 Tu saldo actual en "+str(mon_nombre)+" es:\n\n"
        f"Vencido:     *{mon} {resultado[0]:,.2f}*\n"
        f"Diferido:     *{mon} {resultado[2]:,.2f}*\n"
        f"General:     *{mon} {resultado[1]:,.2f}*\n\n"
        f"Saldos al {str(resultado[3])}\n\n"
        f"(S.E.U.O)\n\n"
        f"Envíe el comando: *pesosresumen* o escriba el codigo de comando '9' para descargar el resumen de cuenta corriente.\n\n"
    )

    respuesta += f"*{nombre_empresa}* {msg_menu}"
    return respuesta

def obtenerFichaDeCereales(nroCelular,  cereal="", clase="0", cosecha=""):

    conn = GestAgroConnection().conn
    cursor = conn.cursor()
    # traigo la información del usuario
    usuario = traerUsuario(0, nroCelular)
    nombre = usuario[3] if usuario else ""
    coope = usuario[0]
    cuenta = usuario[1] if usuario else "0"
    empresa = traerEmpresa(coope)

    nombre_empresa = empresa[5] if empresa else "Empresa no encontrada"
    cereal_codigo = buscarCodigoCereal(cereal)
    print("CEREAL CODIGO: ", cereal_codigo)
    print("OBTENER FICHA DE CEREALES: ", nroCelular, cuenta, cereal, cosecha, clase)

    cursor.execute("SELECT comprob_tipo, comprob_descri, comprob_nro, fecha,  kilos_en, kilos_sal, saldo, preimpreso FROM ficha_cereal WHERE cuenta = %s AND cereal = %s  and  cosecha = %s",
        (cuenta, cereal, cosecha))
    resultado = cursor.fetchall()
    print("RESULTADO FICHA CEREALES: ", str(cuenta)+"-"+str(cereal)+"-"+str(clase)+"-"+str(cosecha))
    respuesta = f"*{nombre}*\nCuenta: {cuenta}\n\nFicha de cereales: "+str(cereal)+"-"+str(clase)+"-"+str(cosecha)+"\n\n"
    for i, fila in enumerate(resultado, 1):
        respuesta += f"*{fila[4]:,.2f}*\n"
        respuesta += f"Kg: *{fila[4]:,.2f}*\n"
        respuesta += f"Kg2: *{fila[5]:,.2f}*\n"
        respuesta += f"Saldo: *{fila[6]:,.2f}*\n\n"

    return respuesta

def buscarCodigoCereal(cereal_input):
    conn = GestAgroConnection().conn
    cursor = conn.cursor()
    if cereal_input.isdigit():
        return cereal_input  # Ya es un código

    # Buscar el código por nombre parecido
    cursor.execute(
        "SELECT codigo_cereal FROM cereal WHERE LOWER(nombre) LIKE %s LIMIT 1",
        ('%' + cereal_input.lower() + '%',)
    )
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None


def obtenerResumenDeCereales(nroCelular, cuenta="0"):
    usuario = traerUsuario(cuenta, 0)
    nombre = usuario[3] if usuario else ""
    coope = usuario[0]
    empresa = traerEmpresa(coope)
    nombre_empresa = empresa[5] if empresa else "Empresa no encontrada"

    conn = GestAgroConnection().conn
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            cereal_descri AS cereal, 
            cosecha,  
            clase_codigo,   
            clase_descri AS clase,  
            kilos1,  
            kilos2,  
            SUM(kilos1 + kilos2) AS saldo 
        FROM resu_cereal 
        WHERE cuenta = %s AND (kilos1 + kilos2) <> 0 
        GROUP BY cereal_descri, cosecha, clase_codigo, clase_descri, kilos1, kilos2 
        ORDER BY orden DESC;
    """, (cuenta,))

    resultado = cursor.fetchall()

    resumen = []
    for fila in resultado:
        resumen.append({
            "cereal": fila[0],
            "cosecha": fila[1],
            "clase_codigo": fila[2],
            "clase": fila[3],
            "kilos1": float(fila[4]),
            "kilos2": float(fila[5]),
            "saldo": float(fila[6])
        })

    datos = {
        "resumen": resumen,
        "nombre": nombre,
        "cuenta": cuenta,
        "empresa": nombre_empresa
    }


    return datos




"""def obtenerResumenDeCereales(nroCelular, cuenta="0"):

    # traigo la información del usuario
    usuario = traerUsuario(cuenta, 0)
    nombre = usuario[3] if usuario else ""
    coope = usuario[0]
    empresa = traerEmpresa(coope)
    nombre_empresa = empresa[5] if empresa else "Empresa no encontrada"

    conn = GestAgroConnection().conn
    cursor = conn.cursor()
    cursor.execute("SELECT cereal_descri AS cereal, cosecha,  clase_codigo,   clase_descri AS clase,  kilos1,  kilos2,  SUM(kilos1 + kilos2) AS saldo FROM   resu_cereal WHERE   cuenta = %s AND (kilos1 + kilos2) <> 0 GROUP BY   cereal_descri, cosecha, clase_codigo, clase_descri, kilos1, kilos2 ORDER BY   orden DESC;",
        (cuenta,))
    resultado = cursor.fetchall()
    respuesta = f"*{nombre}*\nCuenta: {cuenta}\n\n*Este es su resumen de cereales*\n\n"
    for i, fila in enumerate(resultado, 1):
        cereal = fila[0]
        cosecha = fila[1]
        clase = fila[3]
        clase_codigo = fila[2]
        kilos1 = fila[4]
        kilos2 = fila[5]
        saldo = fila[6]

        respuesta += f"*{cereal}* - {clase} (Cod: {clase_codigo}) - {cosecha}: *{saldo:,.2f}*\n\n"

    respuesta += f"{msg_instrucciones}"
    respuesta += f"\n(S.E.U.O)\n\n{nombre_empresa} {msg_menu}"
    return respuesta"""


def obtener_saldo_con_verificacion_token(cuenta, moneda="PES", token=""):
    status = verificarToken(cuenta, token)
    if status == False:
        err = {
            "code": "ERROR",
            "status": 404,
            "description": "El token no es válido, debe autentificarse nuevamente.",
            "name": API_NOMBRE,
            "message": "El token no es válido, debe autentificarse nuevamente.",
        }
        return err
    conn = GestAgroConnection().conn
    cursor = conn.cursor()
    if moneda == "PES":
        cursor.execute("SELECT saldo FROM usuarios WHERE cuenta = %s", (cuenta,))


    elif moneda == "USD":
        cursor.execute("SELECT saldoDolar AS saldo FROM usuarios WHERE cuenta = %s", (cuenta,))
    else:
        conn.close()
        return "Moneda no soportada. Usa 'PES' o 'USD'."
    resultado = cursor.fetchone()
    if moneda == "PES":
        mon = "$"
    elif moneda == "DOL":
        mon = "USD"

    respuesta = f"💰 Tu saldo actual es {mon}{resultado[0]:,.2f}" if resultado else "No se encontró saldo."
    conn.close()
    data = {
        "name": API_NOMBRE,
        "code": "OK",
        "status": 200,
        "description": "Devuelve el saldo en la moneda solicitada.",
        "meneda" : moneda,
        "message":respuesta,
    }

    return data

def buscarEmpresas(celular, coope=0):

    conn = GestAgroConnection().conn
    cursor = conn.cursor()
    query = "SELECT coope, coope_id, coope_name, coope_descri FROM coope WHERE coope = %s"
    cursor.execute(query, (coope,))
    empresa = cursor.fetchone()
    respuesta = empresa
    # Cerrar conexión
    cursor.close()
    conn.close()

    return respuesta

def buscarEmpresasAsociadas(celular, coope=0):

    conn = GestAgroConnection().conn
    cursor = conn.cursor()
    cursor.execute("SELECT coope FROM usuarios WHERE telefono = %s",(celular,))
    datos = cursor.fetchall()
    valores = [item[0] for item in datos]
    # Crear placeholders para la consulta IN
    placeholders = ', '.join(['%s'] * len(valores))
    query = f"SELECT coope, coope_id, coope_name, coope_descri  FROM coope WHERE coope IN ({placeholders})"
    cursor.execute(query, valores)
    resultados = cursor.fetchall()

    # Mostrar los resultados
    respuesta = get_emoji('otros', 'robot')+" *Estimado:* Su celular opera con las siguientes empresas:\n\n"

    for i, fila in enumerate(resultados, 1):
        coope = fila[0]
        nombre_coope = fila[3]
        respuesta += f" {coope} - {nombre_coope} \n"

    respuesta += "\n*Escriba el codigo de la cooperativa con la que desea operar.*\n\n"
    # Cerrar conexión
    cursor.close()
    conn.close()

    return respuesta

def traerEmpresas(celular, coope=0):
    conn = GestAgroConnection().conn
    cursor = conn.cursor()
    cursor.execute("SELECT coope FROM usuarios WHERE telefono = %s", (celular,))
    datos = cursor.fetchall()
    valores = [item[0] for item in datos]
    # Crear placeholders para la consulta IN
    placeholders = ', '.join(['%s'] * len(valores))
    query = f"SELECT coope, coope_id, coope_name, coope_descri, accesoServicioChatBot  FROM coope WHERE coope IN ({placeholders})"
    cursor.execute(query, valores)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    # Mostrar los resultados


    return resultados

def traerUsuario(cuenta="0", nroCelular = 0):

    conn = GestAgroConnection().conn
    cursor = conn.cursor()
    if str(cuenta) == "0" or cuenta == "":
        cursor.execute("SELECT * FROM usuarios WHERE bot = 1 and telefono = %s", (nroCelular,))
    else:
        cursor.execute("SELECT * FROM usuarios WHERE bot = 1 and cuenta = %s", (cuenta,))

    datos = cursor.fetchone()
    resultados = datos
    cursor.close()
    conn.close()
    return resultados

def traerEmpresa(coope):
    conn = GestAgroConnection().conn
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coope WHERE coope = %s", (coope,))
    datos = cursor.fetchone()
    resultados = datos
    cursor.close()
    conn.close()
    return resultados

# MERCADO DE CERAELES DESDE LA PAGINA WEB DE CADA COOPERATIVA


def mercadoCereales(nroCelular, cuenta, tipo="disponible"):
    usuario = traerUsuario(cuenta)
    nombre = usuario[3] if usuario else ""
    coope = usuario[0]
    empresa = traerEmpresa(coope)
    nombre_empresa = empresa[5] if empresa else "Empresa no encontrada"

    conn = WebConnection().conn
    cursor = conn.cursor()
    sql = ""
    if tipo not in ["disponible", "futuro"]:
        return f"🛑 Tipo de mercado no válido. Use 'disponible' o 'futuro'."
    else:
         if tipo == "disponible":
             sql = (
                 "SELECT prod.producto_nombre, m.precio, m.condicion, m.variacion_dia_anterior, p.nombre AS puerto_nombre, "
                 "m.observaciones, m.fecha_cierre, m.id_producto AS id_producto "
                 "FROM mercados_disponible_rosario m "
                 "JOIN productos prod ON prod.id_producto = m.id_producto "
                 "JOIN puertos p ON p.id_puerto = m.id_puerto "
                 "WHERE m.coope = %s "
                 "AND m.fecha_cierre = ("
                 "SELECT MAX(fecha_cierre) FROM mercados_disponible_rosario WHERE coope = %s AND fecha_cierre <= CURDATE()"
                 ") "
                 "AND m.fecha_cierre <= CURDATE()"
             )

         elif tipo =="futuro":

             sql = (
                 "SELECT prod.producto_nombre, mf.precio, mf.condicion, mf.variacion_dia_anterior, "
                 "mf.periodo, mf.observaciones, mf.fecha_cierre, mf.id_producto as id_producto "
                 "FROM mercados_futuros_rosario mf "
                 "JOIN productos prod ON prod.id_producto = mf.id_producto "
                 "WHERE mf.coope = %s AND mf.fecha_cierre = ("
                 "SELECT MAX(fecha_cierre) FROM mercados_futuros_rosario WHERE coope = %s AND fecha_cierre <= CURDATE())"
             )


         else:
            return f"🛑 Tipo de mercado no válido. Use 'disponible' o 'futuro'."

    cursor.execute(sql, (coope, coope))
    resultados = cursor.fetchall()

    fecha_cierre_str = datetime.today().date()   # suponiendo que hay al menos un resultado

    fecha_cierre = datetime.strptime(str(fecha_cierre_str), "%Y-%m-%d").date()
    hace_5_dias = datetime.today().date() - timedelta(days=5)

    if fecha_cierre < hace_5_dias:
        return f"⚠️ Aún no se publicaron datos de cereales. Consulte nuevamente más tarde, o contáctese a la administración.\n\n\n*"+str(nombre_empresa)+"*."

    if resultados is None:
        return f"🛑 No se encontraron datos para el mercado {tipo}."
    cursor.close()
    conn.close()
    ico = ""
    variacion = "📊"
    if resultados:
        if tipo == "disponible":
            moneda = "PES"
            respuesta = f"📈 *MERCADO DISPONIBLE*\n\n"

            for fila in resultados:
                # Mapeo de iconos por id_producto
                iconos = {
                    1: "🌱", 2: "🌻", 3: "🌾", 4: "🌽", 5: "🌾", 6: "🌾", 7: "🌾",
                    8: "🍯", 9: "🍚", 10: "🍵", 11: "🌾", 12: "🌾", 13: "🌱", 14: "🌱"
                }
                ico = iconos.get(fila[7], "🌾")
                variacion = "↔️"
                if float(fila[3]) > 0:
                    variacion = "⬆️"
                elif float(fila[3]) < 0:
                    variacion = "⬇️"

                precio_formateado = "{:,.2f}".format(float(fila[1]))
                nombre_producto = fila[0].strip()

                # Ajusta los anchos según lo que necesites
                respuesta += f"{ico} {nombre_producto.ljust(12)} {precio_formateado.rjust(12)} {str(fila[4]).ljust(10)}\n"

            respuesta += "\n(S.E.U.O)\n"
            respuesta += f"\nFecha de cierre: {fila[6].strftime('%d/%m/%Y')}\n\n*{nombre_empresa}*"
            respuesta += msg_menu
            return respuesta



        elif tipo == "futuro":
            moneda = "USD"
            respuesta = f"📈 *MERCADO FUTURO*\n\n"
            for fila in resultados:
                if fila[7] == 1:
                    ico = "🌱 "
                elif fila[7] == 2:
                    ico = "🌻"
                elif fila[7] == 3:
                    ico = "🌾"
                elif fila[7] == 4:
                    ico = "🌽"
                elif fila[7] == 5:
                    ico = "🌾"
                elif fila[7] == 6:
                    ico = "🌾"
                elif fila[7] == 7:
                    ico = "🌾 "
                elif fila[7] == 8:
                    ico = "🍯"
                elif fila[7] == 9:
                    ico = "🍚"
                elif fila[7] == 10:
                    ico = "🍵"
                elif fila[7] == 11:
                    ico = "🌾"
                elif fila[7] == 12:
                    ico = "🌾"
                elif fila[7] == 13:
                    ico = "🌱"
                elif fila[7] == 14:
                    ico = "🌱"
                else:
                    ico = "🌾"

                if float(fila[2]) > 0:
                    variacion = "⬆️"
                elif float(fila[2]) < 0:
                    variacion = "⬇️"
                else:
                    variacion = "↔️"

                precio = float(fila[1])
                precio_formateado = "{:,.2f}".format(precio)
                nombre_producto = fila[0].strip()

                respuesta += f"{ico:<2} {nombre_producto:<10} {precio_formateado:>10} {str(fila[4]):>10} {variacion:>10}\n"
            respuesta += "\n(S.E.U.O)\n"
            respuesta += f"\nFecha de cierre: {fila[6].strftime('%d/%m/%Y')}\n\n*" + nombre_empresa + "*"
            respuesta += msg_menu
            return respuesta
    else:
        return "No hay datos disponibles para el mercado de cereales."



