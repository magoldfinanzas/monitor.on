import yfinance as yf
import matplotlib.pyplot as plt

tickers = ["GGAL", "YPF"]
data = yf.download(tickers, period="1y")

ggal = data["Close"]["GGAL"].dropna()
ypf = data["Close"]["YPF"].dropna()

ggal_idx = (ggal / ggal.iloc[0]) * 100
ypf_idx = (ypf / ypf.iloc[0]) * 100

ratio = ggal_idx / ypf_idx * 100

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(ratio.index, ratio.values, color="steelblue", linewidth=1.5)
ax.axhline(y=100, color="gray", linestyle="--", linewidth=0.8)
ax.set_title("Ratio GGAL/YPF - Base 100", fontsize=14)
ax.set_xlabel("Fecha")
ax.set_ylabel("Ratio (Base 100)")
ax.grid(True, alpha=0.3)
fig.tight_layout()
plt.show()