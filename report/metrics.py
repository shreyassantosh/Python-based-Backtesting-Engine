import pandas as pd
import numpy as np
import quantstats as qs

class PerformanceMetrics:
    def __init__(self, portfolio_df, trades_df, benchmark_data=None):
        self.portfolio_df = portfolio_df
        self.trades_df = trades_df
        self.benchmark_data = benchmark_data
    
    def calculate_returns(self):
        """Calculate portfolio returns"""
        returns = self.portfolio_df['portfolio_value'].pct_change().dropna()
        return returns
    
    def calculate_metrics(self):
        """Calculate comprehensive performance metrics"""
        returns = self.calculate_returns()
        
        # Basic metrics
        total_return = (self.portfolio_df['portfolio_value'].iloc[-1] / 
                       self.portfolio_df['portfolio_value'].iloc[0] - 1) * 100
        
        # Win/Loss ratio
        winning_trades = self.trades_df[self.trades_df['profit_loss'] > 0] if 'profit_loss' in self.trades_df.columns else pd.DataFrame()
        losing_trades = self.trades_df[self.trades_df['profit_loss'] < 0] if 'profit_loss' in self.trades_df.columns else pd.DataFrame()
        
        win_rate = len(winning_trades) / len(losing_trades) if len(losing_trades) > 0 else 0
        win_loss_ratio = len(winning_trades) / max(len(losing_trades), 1)
        
        # Risk metrics
        sharpe_ratio = qs.stats.sharpe(returns) if len(returns) > 0 else 0
        max_drawdown = qs.stats.max_drawdown(returns) * 100 if len(returns) > 0 else 0
        volatility = returns.std() * np.sqrt(252) * 100 if len(returns) > 0 else 0
        
        # Additional metrics
        total_trades = len(self.trades_df)
        avg_trade_return = self.trades_df['profit_loss'].mean() if 'profit_loss' in self.trades_df.columns and len(self.trades_df) > 0 else 0
        
        metrics = {
            'Total Return (%)': round(total_return, 2),
            'Sharpe Ratio': round(sharpe_ratio, 3),
            'Max Drawdown (%)': round(max_drawdown, 2),
            'Volatility (%)': round(volatility, 2),
            'Win Rate (%)': round(win_rate * 100, 2),
            'Win/Loss Ratio': round(win_loss_ratio, 2),
            'Total Trades': total_trades,
            'Avg Trade Return ($)': round(avg_trade_return, 2)
        }
        
        return metrics
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        metrics = self.calculate_metrics()
        returns = self.calculate_returns()
        
        report = {
            'metrics': metrics,
            'returns': returns,
            'portfolio_value': self.portfolio_df,
            'trades': self.trades_df
        }
        
        return report
