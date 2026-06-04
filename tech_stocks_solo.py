import yfinance as yf

def obtener_precios_tech():
    """
    Descarga precios de cierre del último año para las 4 grandes tecnológicas.
    Formatea los datos para que Recharts pueda graficar múltiples líneas.
    """
    tickers = ["AAPL", "MSFT", "NVDA", "ADBE","MELI","PFE"]
    # Descargamos los datos
    data = yf.download(tickers, period="1y")["Close"]
    
    # Limpiamos valores nulos
    data = data.dropna()
    
    # Formateamos para JSON: una lista donde cada objeto es un día con todos los precios
    # Ejemplo: [{"date": "2024-01-01", "AAPL": 150, "MSFT": 200...}, ...]
    resultado = []
    for index, row in data.iterrows():
        fila = {"date": index.strftime("%Y-%m-%d")}
        for ticker in tickers:
            fila[ticker] = round(float(row[ticker]), 2)
        resultado.append(fila)
        
    return resultado

def obtener_precios_tech_base100():
    """
    Calcula el rendimiento relativo de las acciones (Base 100).
    Permite ver qué activo rindió más porcentualmente, independientemente de su precio.
    """
    tickers = ["AAPL", "MSFT", "NVDA", "ADBE", "MELI", "PFE"]
    data = yf.download(tickers, period="1y")["Close"].dropna()
    
    # Calculamos la base 100: (Precio Actual / Primer Precio de la serie) * 100
    data_base100 = (data / data.iloc[0]) * 100
    
    resultado = []
    for index, row in data_base100.iterrows():
        fila = {"date": index.strftime("%Y-%m-%d")}
        for ticker in tickers:
            fila[ticker] = round(float(row[ticker]), 2)
        resultado.append(fila)
        
    return resultado
