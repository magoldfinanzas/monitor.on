import os
import glob
import datetime
import requests
import urllib3
import pandas as pd
import scipy.optimize as optimize
from io import StringIO

# Desactivar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_data912_prices():
    """Conecta a la API de data912.com y obtiene los precios."""
    url = "https://data912.com/live/arg_corp"
    response = requests.get(url, timeout=30, verify=False)
    response.raise_for_status()
    return pd.DataFrame(response.json())

def calcular_metricas_bono(fechas, flujos, precio_actual):
    """Calcula la TIR y la Duration (Macaulay)."""
    hoy = pd.Timestamp(datetime.date.today())
    dias_y_flujos = []
    for fecha, flujo in zip(fechas, flujos):
        dias = (fecha - hoy).days
        if dias > 0:
            dias_y_flujos.append((dias, flujo))
            
    if not dias_y_flujos or precio_actual <= 0:
        return None, None
        
    def ecuacion_valor_presente(r):
        # Evitar valores de r que invaliden la potencia
        if r <= -1: return 1e10 
        vp = sum([flujo / ((1 + r) ** (dias / 365.25)) for dias, flujo in dias_y_flujos])
        return vp - precio_actual

    try:
        tir = optimize.newton(ecuacion_valor_presente, 0.10, maxiter=1000)
        # Macaulay Duration
        numerador_duration = sum([ (d/365.25) * (f / ((1 + tir) ** (d/365.25))) for d, f in dias_y_flujos])
        duration = numerador_duration / precio_actual
        return tir * 100, duration
    except:
        return None, None

def obtener_datos_on():
    """Lógica principal para recolectar datos y calcular métricas."""
    carpeta = os.path.join(os.path.dirname(__file__), "flujos")
    archivos = glob.glob(os.path.join(carpeta, "*.csv"))
    
    data_list = []
    metadata_keys = set()
    
    for archivo in archivos:
        ticker = os.path.basename(archivo).replace(".csv", "")
        with open(archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            
        metadatos = {"Ticker": ticker}
        inicio_flujos = 0
        for i, linea in enumerate(lineas):
            linea = linea.strip()
            if linea == "# FLUJOS":
                inicio_flujos = i + 1
                break
            if "," in linea and not linea.startswith("#"):
                parts = linea.split(",", 1)
                if len(parts) == 2:
                    clave, valor = parts[0].strip(), parts[1].strip()
                    metadatos[clave] = valor
                    metadata_keys.add(clave)
            
        try:
            df_flujos = pd.read_csv(StringIO("".join(lineas[inicio_flujos:])))
            df_flujos["fecha"] = pd.to_datetime(df_flujos["fecha"])
            df_flujos["flujo_total"] = df_flujos["interes"] + df_flujos["amortizacion"]
            
            pagos_amort = df_flujos[df_flujos["amortizacion"] > 0]
            metadatos["Estructura"] = "Bullet" if len(pagos_amort) == 1 else "Amortizable"
            
            data_list.append({"ticker": ticker, "metadata": metadatos, "df_flujos": df_flujos})
        except: pass

    try:
        df_precios = get_data912_prices()
    except: return []

    final_rows = []
    for item in data_list:
        ticker = item["ticker"]
        fila_online = df_precios[df_precios['symbol'] == ticker]
        precio = fila_online['c'].values[0] if not fila_online.empty else 0.0
        
        if precio > 0:
            tir, duration = calcular_metricas_bono(item["df_flujos"]["fecha"], 
                                                 item["df_flujos"]["flujo_total"], 
                                                 precio)
            if tir is not None:
                row = item["metadata"].copy()
                row["TIR"] = round(tir, 2)
                row["Duration"] = round(duration, 2)
                row["Precio USD"] = precio
                final_rows.append(row)
    
    return final_rows, sorted(list(metadata_keys))

if __name__ == "__main__":
    # Importamos plotly solo si el script se ejecuta directamente
    import plotly.express as px
    
    final_rows, metadata_keys = obtener_datos_on()
    
    if final_rows:
        df_final = pd.DataFrame(final_rows)
        hover_cols = metadata_keys + ["TIR", "Duration", "Precio USD"]
        
        fig = px.scatter(
            df_final, x="Duration", y="TIR", color="ley",
            color_discrete_map={"NY": "red", "AR": "blue"},
            symbol="Estructura",
            symbol_map={"Bullet": "diamond", "Amortizable": "circle"},
            text="Ticker",
            hover_data=hover_cols,
            title="Analisis de Obligaciones Negociables: TIR vs Duration",
            template="plotly_white",
            labels={"TIR": "TIR (%)", "Duration": "Duration (Años)", "ley": "Ley", "Estructura": "Tipo"}
        )

        fig.update_traces(
            marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')),
            textposition='top center'
        )
        
        print(df_final[["Ticker", "TIR", "Duration", "Precio USD"]].to_string(index=False))
        fig.show()
    else:
        print("No se pudieron calcular datos.")
