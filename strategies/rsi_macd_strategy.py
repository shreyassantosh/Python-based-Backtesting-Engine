import pandas as pd
import numpy as np
import ta

class RSIMACDStrategy:
    def __init__(self, rsi_period=14, rsi_oversold=30, rsi_overbought=70,
                 macd_fast=12, macd_slow=26, macd_signal=9):
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
    
    def calculate_indicators(self, data):
        """Calculate RSI and MACD indicators"""
        df = data.copy()
        
        # RSI calculation
        df['rsi'] = ta.momentum.RSIIndicator(
            close=df['close'], 
            window=self.rsi_period
        ).rsi()
        
        # MACD calculation
        macd = ta.trend.MACD(
            close=df['close'],
            window_fast=self.macd_fast,
            window_slow=self.macd_slow,
            window_sign=self.macd_signal
        )
        
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()
        
        # Moving averages
        df['sma_20'] = ta.trend.SMAIndicator(df['close'], window=20).sma_indicator()
        df['sma_50'] = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()
        
        return df
    
    def generate_signals(self, data):
        """Generate buy/sell signals based on RSI and MACD"""
        df = self.calculate_indicators(data)
        
        # Initialize signal columns
        df['buy_signal'] = False
        df['sell_signal'] = False
        
        # MACD crossover conditions
        macd_cross_above = (df['macd'] > df['macd_signal']) & \
                          (df['macd'].shift(1) <= df['macd_signal'].shift(1))
        macd_cross_below = (df['macd'] < df['macd_signal']) & \
                          (df['macd'].shift(1) >= df['macd_signal'].shift(1))
        
        # Buy signals: RSI < oversold AND MACD crossover
        df['buy_signal'] = (df['rsi'] < self.rsi_oversold) & macd_cross_above
        
        # Sell signals: RSI > overbought OR MACD cross under
        df['sell_signal'] = (df['rsi'] > self.rsi_overbought) | macd_cross_below
        
        return df
