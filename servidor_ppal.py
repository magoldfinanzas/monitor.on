import json
from wsgiref.simple_server import make_server

# IMPORTANTE: Aquí importamos la función desde el archivo ggal_ypf_solo.py
from ggal_ypf_solo import obtener_datos_ratio
from tech_stocks_solo import obtener_precios_tech, obtener_precios_tech_base100
from ON.N5_solo import obtener_datos_on

# --- CONTROLADOR DEL SERVIDOR ---

def aplicacion_web(environ, responder):
    """
    Función principal del servidor que actúa como 'telefonista' 
    repartiendo las peticiones a las funciones correspondientes.
    """
    path = environ.get('PATH_INFO', '')
    metodo = environ.get('REQUEST_METHOD', '')

    # Cabeceras estándar para permitir CORS (conexión con React) y formato JSON
    headers = [
        ('Content-Type', 'application/json'),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type')
    ]

    # Manejo de la petición OPTIONS (pre-vuelo de seguridad del navegador)
    if metodo == 'OPTIONS':
        responder('200 OK', headers)
        return [b""]

    # ENRUTADOR: Aquí decidimos qué hacer según la URL
    if path == '/api/ratio':
        try:
            datos = obtener_datos_ratio()
            responder('200 OK', headers)
            return [json.dumps(datos).encode('utf-8')]
        except Exception as e:
            responder('500 Error', headers)
            return [json.dumps({"error": str(e)}).encode('utf-8')]

    elif path == '/api/tech':
        try:
            # Llamamos a la nueva función de tecnología
            datos = obtener_precios_tech()
            responder('200 OK', headers)
            return [json.dumps(datos).encode('utf-8')]
        except Exception as e:
            responder('500 Error', headers)
            return [json.dumps({"error": str(e)}).encode('utf-8')]

    elif path == '/api/tech-base100':
        try:
            datos = obtener_precios_tech_base100()
            responder('200 OK', headers)
            return [json.dumps(datos).encode('utf-8')]
        except Exception as e:
            responder('500 Error', headers)
            return [json.dumps({"error": str(e)}).encode('utf-8')]

    elif path == '/api/ons':
        try:
            # Obtenemos solo la primera parte (los datos), ignorando las keys de metadatos
            datos, _ = obtener_datos_on()
            responder('200 OK', headers)
            return [json.dumps(datos).encode('utf-8')]
        except Exception as e:
            responder('500 Error', headers)
            return [json.dumps({"error": str(e)}).encode('utf-8')]

    # Si no coincide ninguna ruta
    responder('404 Not Found', headers)
    return [json.dumps({"error": "Ruta no encontrada"}).encode('utf-8')]

# --- ARRANQUE DEL SERVIDOR ---

if __name__ == '__main__':
    import os
    puerto = int(os.getenv("PORT", "8000"))
    httpd = make_server('', puerto, aplicacion_web)
    print(f"Servidor PRINCIPAL activo en http://0.0.0.0:{puerto}")
    print(f"Escuchando conexiones...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
