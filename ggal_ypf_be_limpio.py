import yfinance as yf
import json
from wsgiref.simple_server import make_server

# --- LÓGICA DE DATOS (Funcional) ---

def obtener_datos_ratio():
    """Descarga y procesa el ratio GGAL/YPF"""
    tickers = ["GGAL", "YPF"]
    data = yf.download(tickers, period="1y")
    
    # Precios de cierre
    ggal = data["Close"]["GGAL"].dropna()
    ypf = data["Close"]["YPF"].dropna()
    
    # Índices base 100
    ggal_idx = (ggal / ggal.iloc[0]) * 100
    ypf_idx = (ypf / ypf.iloc[0]) * 100
    
    # Ratio
    ratio = ggal_idx / ypf_idx * 100
    
    # Formato para JSON
    return [
        {"date": d.strftime("%Y-%m-%d"), "ratio": round(float(v), 2)} 
        for d, v in ratio.items()
    ]

# --- LÓGICA DEL SERVIDOR (Sin Clases) ---

def aplicacion_web(environ, responder):
    """
    Esta función es el 'servidor'. Recibe la petición y devuelve la respuesta.
    """
    path = environ.get('PATH_INFO', '')
    metodo = environ.get('REQUEST_METHOD', '')

    # Manejo de CORS (para que React pueda conectar)
    headers = [
        ('Content-Type', 'application/json'),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type')
    ]

    # Si es una petición de control (OPTIONS), respondemos OK
    if metodo == 'OPTIONS':
        responder('200 OK', headers)
        return [b""]

    # Si piden la ruta correcta
    if path == '/api/ratio':
        try:
            datos = obtener_datos_ratio()
            cuerpo_respuesta = json.dumps(datos).encode('utf-8')
            responder('200 OK', headers)
            return [cuerpo_respuesta]
        except Exception as e:
            responder('500 Internal Server Error', headers)
            return [json.dumps({"error": str(e)}).encode('utf-8')]

    # Cualquier otra ruta
    responder('404 Not Found', headers)
    return [json.dumps({"error": "No encontrado"}).encode('utf-8')]

# --- ARRANQUE ---

if __name__ == '__main__':
    puerto = 8000
    servidor = make_server('', puerto, aplicacion_web)
    print(f"Servidor LIMPIO corriendo en http://localhost:{puerto}/api/ratio")
    print("Presiona Ctrl+C para salir")
    servidor.serve_forever()

# --- JUSTIFICATIVOS ---
# 1. yfinance: Obtención de datos financieros (en requirements.txt).
# 2. json: Conversión de datos a formato estándar web (Standard Lib).
# 3. wsgiref: Servidor web basado en funciones (Standard Lib). Permite evitar el uso de clases.
