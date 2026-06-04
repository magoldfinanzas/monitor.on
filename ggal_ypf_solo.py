import yfinance as yf

# Este archivo contiene ÚNICAMENTE la lógica de cálculo financiero.
# No contiene nada relacionado con servidores web.

def obtener_datos_ratio():
    """
    Descarga datos de GGAL y YPF, calcula el ratio base 100 y 
    devuelve una lista formateada para JSON.
    """
    tickers = ["GGAL", "YPF"]
    # Descarga
    data = yf.download(tickers, period="1y")
    
    # Procesamiento
    ggal = data["Close"]["GGAL"].dropna()
    ypf = data["Close"]["YPF"].dropna()
    
    # Índices base 100
    ggal_idx = (ggal / ggal.iloc[0]) * 100
    ypf_idx = (ypf / ypf.iloc[0]) * 100
    
    # Cálculo de ratio
    ratio = ggal_idx / ypf_idx * 100
    
    # Formateo para que React lo entienda (Lista de diccionarios)
    return [
        {"date": d.strftime("%Y-%m-%d"), "ratio": round(float(v), 2)} 
        for d, v in ratio.items()
    ]
