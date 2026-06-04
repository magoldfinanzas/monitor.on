import yfinance as yf
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- SECCIÓN DE PROCESAMIENTO DE DATOS ---

def get_ratio_data():
    """
    Descarga datos de GGAL y YPF, calcula el ratio base 100 y 
    devuelve una lista formateada para JSON.
    """
    tickers = ["GGAL", "YPF"]
    # Descargamos los datos históricos del último año
    data = yf.download(tickers, period="1y")
    
    # Extraemos los precios de cierre y eliminamos valores nulos
    ggal = data["Close"]["GGAL"].dropna()
    ypf = data["Close"]["YPF"].dropna()
    
    # Calculamos el índice base 100 para cada acción (precio / primer_precio * 100)
    ggal_idx = (ggal / ggal.iloc[0]) * 100
    ypf_idx = (ypf / ypf.iloc[0]) * 100
    
    # Calculamos el ratio entre ambos índices
    ratio = ggal_idx / ypf_idx * 100
    
    # Formateamos los datos en una lista de diccionarios que React pueda entender
    # Ejemplo: [{"date": "2023-01-01", "ratio": 105.2}, ...]
    formatted_data = []
    for date, value in ratio.items():
        formatted_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "ratio": round(float(value), 2)
        })
    return formatted_data

# --- SECCIÓN DEL SERVIDOR WEB ---

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """
    Maneja las peticiones HTTP que llegan desde el navegador o React.
    """
    
    def do_OPTIONS(self):
        """
        Maneja la petición 'preflight' de CORS. Es necesaria para que el
        navegador permita a React comunicarse con este servidor.
        """
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.end_headers()

    def do_GET(self):
        """
        Maneja las peticiones GET (cuando se pide información).
        """
        # Definimos que solo responda en la ruta /api/ratio
        if self.path == '/api/ratio':
            try:
                # 1. Obtenemos los datos financieros procesados
                data = get_ratio_data()
                
                # 2. Preparamos la respuesta exitosa (Código 200)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                # Permitimos que cualquier origen (como localhost:5173) lea los datos
                self.send_header('Access-Control-Allow-Origin', '*') 
                self.end_headers()
                
                # 3. Convertimos la lista de Python a un string JSON y lo enviamos
                self.wfile.write(json.dumps(data).encode('utf-8'))
                
            except Exception as e:
                # Manejo básico de errores si algo falla en la descarga o proceso
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {"error": str(e)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            # Si se pide cualquier otra ruta, devolvemos un 404
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Ruta no encontrada. Usa /api/ratio"}).encode('utf-8'))

def run_server(port=8000):
    """
    Inicia el servidor en el puerto especificado.
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Backend Servidor corriendo en http://localhost:{port}")
    print(f"Endpoint de datos disponible en: http://localhost:{port}/api/ratio")
    print("Presiona Ctrl+C para detener el servidor")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Servidor detenido.")

if __name__ == '__main__':
    run_server()

# --- JUSTIFICATIVO DE LIBRERÍAS ---
# 1. yfinance: Se utiliza para descargar datos reales del mercado financiero desde Yahoo Finance.
#    Es la fuente principal de información para este script.
# 2. json: Librería estándar de Python para convertir objetos (listas/diccionarios) a formato JSON,
#    que es el estándar de comunicación en la web y lo que React espera recibir.
# 3. http.server: Librería estándar de Python para crear un servidor web básico. Se utiliza aquí
#    para evitar la instalación de dependencias externas como Flask o FastAPI, manteniendo el
#    entorno limpio según lo solicitado.

