import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self):
        self.cache = {}
    
    def fetch_stock_data(self, ticker, start_date, end_date):
        """Fetch historical stock data from Yahoo Finance"""
        cache_key = f"{ticker}_{start_date}_{end_date}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            
            if data.empty:
                raise ValueError(f"No data found for ticker {ticker}")
            
            # Clean and prepare data
            data = data.dropna()
            data.columns = [col.lower() for col in data.columns]
            
            self.cache[cache_key] = data
            return data
            
        except Exception as e:
            raise Exception(f"Error fetching data for {ticker}: {str(e)}")
    
    def get_available_tickers(self):
        """Return list of popular stock tickers for selection"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
            'META', 'NVDA', 'JPM', 'JNJ', 'V',
            'SPY', 'QQQ', 'BTC-USD', 'ETH-USD'
        ]
