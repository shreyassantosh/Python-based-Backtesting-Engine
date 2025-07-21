import pandas as pd
import numpy as np
from datetime import datetime

class BacktestEngine:
    def __init__(self, initial_capital=10000, commission=0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.reset()
    
    def reset(self):
        """Reset backtesting state"""
        self.capital = self.initial_capital
        self.position = 0
        self.entry_price = 0
        self.trades = []
        self.portfolio_value = []
        self.dates = []
    
    def execute_backtest(self, data_with_signals):
        """Execute backtest based on signals"""
        self.reset()
        df = data_with_signals.copy()
        
        for index, row in df.iterrows():
            current_price = row['close']
            
            # Calculate current portfolio value
            portfolio_val = self.capital + (self.position * current_price)
            self.portfolio_value.append(portfolio_val)
            self.dates.append(index)
            
            # Process buy signals
            if row['buy_signal'] and self.position == 0:
                shares_to_buy = int(self.capital / (current_price * (1 + self.commission)))
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price * (1 + self.commission)
                    self.position = shares_to_buy
                    self.capital -= cost
                    self.entry_price = current_price
                    
                    self.trades.append({
                        'date': index,
                        'type': 'BUY',
                        'price': current_price,
                        'shares': shares_to_buy,
                        'value': cost
                    })
            
            # Process sell signals
            elif row['sell_signal'] and self.position > 0:
                proceeds = self.position * current_price * (1 - self.commission)
                profit_loss = proceeds - (self.position * self.entry_price * (1 + self.commission))
                
                self.trades.append({
                    'date': index,
                    'type': 'SELL',
                    'price': current_price,
                    'shares': self.position,
                    'value': proceeds,
                    'profit_loss': profit_loss
                })
                
                self.capital += proceeds
                self.position = 0
                self.entry_price = 0
        
        # Create portfolio DataFrame
        portfolio_df = pd.DataFrame({
            'date': self.dates,
            'portfolio_value': self.portfolio_value
        })
        portfolio_df.set_index('date', inplace=True)
        
        return portfolio_df, pd.DataFrame(self.trades)
