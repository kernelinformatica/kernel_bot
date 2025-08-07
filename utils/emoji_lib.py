# emoji_lib.py

emojis = {
    "estado": {
        "ok": "✅",
        "conectado": "🟢",
        "pendiente": "⏳",
        "error": "❌",
        "advertencia": "⚠️",
        "bloqueado": "🔒"
    },
    "acciones": {
        "enviando": "📤",
        "recibido": "📥",
        "buscando": "🔍",
        "procesando": "🔄",
        "inicio": "🚀"
    },
    "usuario": {
        "usuario": "👤",
        "grupo": "👥",
        "admin": "🛡️",
        "dev": "🧑‍💻",
        "ok": "👌",
    },
    "documentos": {
        "archivo": "📄",
        "reporte": "📊",
        "carpeta": "🗂️",
        "dato": "🧠"
    },
    "notificacion": {
        "info": "💬",
        "alerta": "📢",
        "fijado": "📌",
        "nuevo": "🆕"
    },
    "monedas": {
        "peso": "💰",
        "dolar": "💵",
        "euro": "💶",
        "libra": "💷",
        "yen": "💴"
    },
    "acciones_usuario": {
        "login": "🔑",
        "logout": "🚪",
        "registrar": "📝",
        "editar": "✏️",
        "eliminar": "🗑️"
    },
    "errores": {
        "error": "❗",
        "error_critico": "🚨",
        "error_conexion": "🌐",
        "error_autenticacion": "🔐",
        "error_permiso": "🚫"
    },
    "numeros": {
        "uno": "1️⃣",
        "dos": "2️⃣",
        "tres": "3️⃣",
        "cuatro": "4️⃣",
        "cinco": "5️⃣",
        "seis": "6️⃣",
        "siete": "7️⃣",
        "ocho": "8️⃣",
        "nueve": "9️⃣",
        "cero": "0️⃣"
    },
    "general": {
        "guardar": "💾",
        "cancelar": "❌",
        "confirmar": "✔️",
        "buscar": "🔎",
        "actualizar": "🔃"
    },
    "mercados": {
        "mercado": "📈",
        "cereales": "🌾",
        "soja": "🌱",
        "maiz": "🌽",
        "girasol": "🌻",
        "granos": "🌾",
        "sorgo": "🌾",
        "trigo": "🌾",
        "lino": "🌾",
        "algodon": "🌾",
        "arroz": "🍚",
        "miel": "🍯",
        "cebada": "🌾",
        "avena": "🌾",
        "colza": "🌾",
    },
    "flechas": {
        "arriba": "⬆️",
        "abajo": "⬇️",
        "izquierda": "⬅️",
        "derecha": "➡️",
        "circular": "🔄",
        "diagonal": "↗️",
        "igual" : "↔️"
    },
    "variaciones": {
        "aumento": "📈",
        "disminucion": "📉",
        "estable": "📊",
        "volatilidad": "⚡"
    },
    "otros": {
        "robot": "🤖",
        "ok_limpio": "🧼",
        "check": "☑️",
        "tip": "✨",
        "error_critico": "🛑",
        "herramienta": "🧰"
    },


}


def get_emoji(categoria: str, clave: str) -> str:
    return emojis.get(categoria, {}).get(clave, "")
