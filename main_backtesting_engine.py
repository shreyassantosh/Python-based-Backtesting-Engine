import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.subplots as sp
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class TechnicalIndicators:
    """Class to calculate various technical indicators"""
    
    @staticmethod
    def rsi(prices, window=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(prices, fast=12, slow=26, signal=9):
        """Calculate MACD, MACD Signal, and MACD Histogram"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def moving_average(prices, window):
        """Calculate Simple Moving Average"""
        return prices.rolling(window=window).mean()
    
    @staticmethod
    def bollinger_bands(prices, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        return upper_band, sma, lower_band

class BacktestingEngine:
    """Main backtesting engine class"""
    
    def __init__(self, ticker, start_date, end_date, initial_capital=100000):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.data = None
        self.trades = []
        self.portfolio_value = []
        self.positions = []
        
    def fetch_data(self):
        """Fetch historical stock data"""
        try:
            stock = yf.Ticker(self.ticker)
            self.data = stock.history(start=self.start_date, end=self.end_date)
            return True
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return False
    
    def calculate_indicators(self):
        """Calculate all technical indicators"""
        if self.data is None or self.data.empty:
            return False
        
        # RSI
        self.data['RSI'] = TechnicalIndicators.rsi(self.data['Close'])
        
        # MACD
        macd, signal, histogram = TechnicalIndicators.macd(self.data['Close'])
        self.data['MACD'] = macd
        self.data['MACD_Signal'] = signal
        self.data['MACD_Histogram'] = histogram
        
        # Moving Averages
        self.data['MA_20'] = TechnicalIndicators.moving_average(self.data['Close'], 20)
        self.data['MA_50'] = TechnicalIndicators.moving_average(self.data['Close'], 50)
        
        # Bollinger Bands
        upper, middle, lower = TechnicalIndicators.bollinger_bands(self.data['Close'])
        self.data['BB_Upper'] = upper
        self.data['BB_Middle'] = middle
        self.data['BB_Lower'] = lower
        
        return True
    
    def generate_signals(self, strategy_params):
        """Generate buy/sell signals based on strategy parameters"""
        self.data['Signal'] = 0
        self.data['Position'] = 0
        
        for i in range(1, len(self.data)):
            buy_condition = False
            sell_condition = False
            
            # RSI conditions
            if strategy_params['use_rsi']:
                rsi_buy = self.data['RSI'].iloc[i] < strategy_params['rsi_buy_threshold']
                rsi_sell = self.data['RSI'].iloc[i] > strategy_params['rsi_sell_threshold']
            else:
                rsi_buy = rsi_sell = False
            
            # MACD conditions
            if strategy_params['use_macd']:
                macd_crossover = (self.data['MACD'].iloc[i] > self.data['MACD_Signal'].iloc[i] and 
                                self.data['MACD'].iloc[i-1] <= self.data['MACD_Signal'].iloc[i-1])
                macd_crossunder = (self.data['MACD'].iloc[i] < self.data['MACD_Signal'].iloc[i] and 
                                 self.data['MACD'].iloc[i-1] >= self.data['MACD_Signal'].iloc[i-1])
            else:
                macd_crossover = macd_crossunder = False
            
            # Moving Average conditions
            if strategy_params['use_ma']:
                ma_buy = self.data['Close'].iloc[i] > self.data['MA_20'].iloc[i]
                ma_sell = self.data['Close'].iloc[i] < self.data['MA_20'].iloc[i]
            else:
                ma_buy = ma_sell = False
            
            # Combine conditions based on strategy logic
            if strategy_params['logic'] == 'AND':
                buy_condition = all([
                    rsi_buy if strategy_params['use_rsi'] else True,
                    macd_crossover if strategy_params['use_macd'] else True,
                    ma_buy if strategy_params['use_ma'] else True
                ])
                sell_condition = any([
                    rsi_sell if strategy_params['use_rsi'] else False,
                    macd_crossunder if strategy_params['use_macd'] else False,
                    ma_sell if strategy_params['use_ma'] else False
                ])
            else:  # OR logic
                buy_condition = any([
                    rsi_buy if strategy_params['use_rsi'] else False,
                    macd_crossover if strategy_params['use_macd'] else False,
                    ma_buy if strategy_params['use_ma'] else False
                ])
                sell_condition = any([
                    rsi_sell if strategy_params['use_rsi'] else False,
                    macd_crossunder if strategy_params['use_macd'] else False,
                    ma_sell if strategy_params['use_ma'] else False
                ])
            
            # Generate signals
            current_position = self.data['Position'].iloc[i-1]
            
            if buy_condition and current_position == 0:
                self.data.loc[self.data.index[i], 'Signal'] = 1  # Buy signal
                self.data.loc[self.data.index[i], 'Position'] = 1
            elif sell_condition and current_position == 1:
                self.data.loc[self.data.index[i], 'Signal'] = -1  # Sell signal
                self.data.loc[self.data.index[i], 'Position'] = 0
            else:
                self.data.loc[self.data.index[i], 'Position'] = current_position
    
    def simulate_trading(self):
        """Simulate trading based on generated signals"""
        self.trades = []
        cash = self.initial_capital
        shares = 0
        self.portfolio_value = []
        
        for i in range(len(self.data)):
            current_price = self.data['Close'].iloc[i]
            signal = self.data['Signal'].iloc[i]
            
            if signal == 1 and cash > 0:  # Buy
                shares_to_buy = int(cash / current_price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    cash -= cost
                    shares += shares_to_buy
                    
                    trade = {
                        'Date': self.data.index[i],
                        'Action': 'BUY',
                        'Price': current_price,
                        'Shares': shares_to_buy,
                        'Cost': cost,
                        'Cash': cash,
                        'Total_Shares': shares
                    }
                    self.trades.append(trade)
            
            elif signal == -1 and shares > 0:  # Sell
                revenue = shares * current_price
                cash += revenue
                
                trade = {
                    'Date': self.data.index[i],
                    'Action': 'SELL',
                    'Price': current_price,
                    'Shares': shares,
                    'Revenue': revenue,
                    'Cash': cash,
                    'Total_Shares': 0
                }
                self.trades.append(trade)
                shares = 0
            
            # Calculate portfolio value
            portfolio_val = cash + (shares * current_price)
            self.portfolio_value.append(portfolio_val)
        
        self.data['Portfolio_Value'] = self.portfolio_value
    
    def calculate_performance_metrics(self):
        """Calculate comprehensive performance metrics"""
        if not self.portfolio_value:
            return {}
        
        # Basic returns
        returns = pd.Series(self.portfolio_value).pct_change().dropna()
        cumulative_return = (self.portfolio_value[-1] / self.initial_capital - 1) * 100
        
        # Win/Loss Ratio
        winning_trades = [t for t in self.trades if t['Action'] == 'SELL']
        if len(winning_trades) > 1:
            trade_returns = []
            for i in range(0, len(winning_trades), 2):
                if i + 1 < len(winning_trades):
                    buy_price = winning_trades[i]['Price'] if winning_trades[i]['Action'] == 'BUY' else winning_trades[i+1]['Price']
                    sell_price = winning_trades[i+1]['Price'] if winning_trades[i+1]['Action'] == 'SELL' else winning_trades[i]['Price']
                    trade_return = (sell_price - buy_price) / buy_price
                    trade_returns.append(trade_return)
            
            wins = len([r for r in trade_returns if r > 0])
            losses = len([r for r in trade_returns if r <= 0])
            win_loss_ratio = wins / losses if losses > 0 else float('inf')
        else:
            win_loss_ratio = 0
        
        # Sharpe Ratio (assuming risk-free rate of 2%)
        risk_free_rate = 0.02 / 252  # Daily risk-free rate
        excess_returns = returns - risk_free_rate
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / returns.std() if returns.std() != 0 else 0
        
        # Maximum Drawdown
        peak = np.maximum.accumulate(self.portfolio_value)
        drawdown = (np.array(self.portfolio_value) - peak) / peak
        max_drawdown = np.min(drawdown) * 100
        
        # Additional metrics
        total_trades = len(self.trades)
        volatility = returns.std() * np.sqrt(252) * 100
        
        return {
            'Cumulative Return (%)': round(cumulative_return, 2),
            'Win/Loss Ratio': round(win_loss_ratio, 2),
            'Sharpe Ratio': round(sharpe_ratio, 2),
            'Max Drawdown (%)': round(max_drawdown, 2),
            'Total Trades': total_trades,
            'Volatility (%)': round(volatility, 2),
            'Final Portfolio Value': round(self.portfolio_value[-1], 2)
        }
