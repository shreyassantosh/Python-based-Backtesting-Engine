# 📊 Technical Analysis Dashboard

This Streamlit app provides a simple dashboard to analyze stock data using popular technical indicators like RSI and MACD. It helps identify potential **buy** and **sell** signals for traders and technical analysts.

---

## 🚀 Features

- 📈 Real-time stock price fetching via `yfinance`
- 📊 RSI (Relative Strength Index) & MACD indicators
- 📉 Interactive stock price chart
- 📆 Date input for backtesting
- 📍 Buy/sell signal highlighting

---

## 📌 How it works

- The app fetches historical stock data using Yahoo Finance.
- Computes:
  - **RSI** – to detect overbought/oversold conditions.
  - **MACD** – to detect trend direction and momentum.
- Suggests **Buy** when:
  - RSI < 30 (oversold) AND MACD is bullish.
- Suggests **Sell** when:
  - RSI > 70 (overbought) AND MACD is bearish.

---

## 🛠️ Installation (Local)

```bash
git clone https://github.com/shreyassantosh/Python-Backtesting-Engine.git
cd backtesting-dashboard
pip install -r requirements.txt
streamlit run backtesting_app.py
