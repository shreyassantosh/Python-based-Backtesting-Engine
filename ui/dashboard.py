import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from fpdf import FPDF
import base64

class Dashboard:
    def __init__(self):
        self.setup_page()
    
    def setup_page(self):
        """Configure Streamlit page"""
        st.set_page_config(
            page_title="Backtesting Engine",
            page_icon="📈",
            layout="wide"
        )
    
    def create_price_chart(self, data, trades_df):
        """Create interactive price chart with buy/sell markers"""
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=('Price & Signals', 'RSI', 'MACD'),
            row_width=[0.5, 0.2, 0.3]
        )
        
        # Price chart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Price'
            ), row=1, col=1
        )
        
        # Moving averages
        fig.add_trace(
            go.Scatter(x=data.index, y=data['sma_20'], 
                      name='SMA 20', line=dict(color='orange')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=data.index, y=data['sma_50'], 
                      name='SMA 50', line=dict(color='blue')),
            row=1, col=1
        )
        
        # Buy/Sell markers
        if not trades_df.empty:
            buy_trades = trades_df[trades_df['type'] == 'BUY']
            sell_trades = trades_df[trades_df['type'] == 'SELL']
            
            if not buy_trades.empty:
                fig.add_trace(
                    go.Scatter(
                        x=buy_trades['date'],
                        y=buy_trades['price'],
                        mode='markers',
                        marker=dict(symbol='triangle-up', size=12, color='green'),
                        name='Buy Signal'
                    ), row=1, col=1
                )
            
            if not sell_trades.empty:
                fig.add_trace(
                    go.Scatter(
                        x=sell_trades['date'],
                        y=sell_trades['price'],
                        mode='markers',
                        marker=dict(symbol='triangle-down', size=12, color='red'),
                        name='Sell Signal'
                    ), row=1, col=1
                )
        
        # RSI
        fig.add_trace(
            go.Scatter(x=data.index, y=data['rsi'], name='RSI', line=dict(color='purple')),
            row=2, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        fig.add_trace(
            go.Scatter(x=data.index, y=data['macd'], name='MACD', line=dict(color='blue')),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=data.index, y=data['macd_signal'], name='Signal', line=dict(color='red')),
            row=3, col=1
        )
        fig.add_trace(
            go.Bar(x=data.index, y=data['macd_histogram'], name='Histogram', marker_color='gray'),
            row=3, col=1
        )
        
        fig.update_layout(height=800, showlegend=True)
        fig.update_xaxes(rangeslider_visible=False)
        
        return fig
    
    def create_performance_chart(self, portfolio_df, benchmark_data=None):
        """Create portfolio performance chart"""
        fig = go.Figure()
        
        # Portfolio performance
        fig.add_trace(
            go.Scatter(
                x=portfolio_df.index,
                y=portfolio_df['portfolio_value'],
                mode='lines',
                name='Portfolio',
                line=dict(color='blue', width=2)
            )
        )
        
        # Benchmark comparison if provided
        if benchmark_data is not None:
            normalized_benchmark = benchmark_data['close'] / benchmark_data['close'].iloc[0] * portfolio_df['portfolio_value'].iloc[0]
            fig.add_trace(
                go.Scatter(
                    x=benchmark_data.index,
                    y=normalized_benchmark,
                    mode='lines',
                    name='Benchmark',
                    line=dict(color='gray', dash='dash')
                )
            )
        
        fig.update_layout(
            title='Portfolio Performance',
            xaxis_title='Date',
            yaxis_title='Portfolio Value ($)',
            height=400
        )
        
        return fig
    
    def export_to_csv(self, trades_df, metrics):
        """Export trade logs and metrics to CSV"""
        csv_buffer = trades_df.to_csv(index=False)
        
        # Add metrics summary
        metrics_df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
        csv_buffer += "\n\nPerformance Metrics:\n"
        csv_buffer += metrics_df.to_csv(index=False)
        
        return csv_buffer
    
    def export_to_pdf(self, metrics, trades_df):
        """Export performance summary to PDF"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Backtesting Performance Report', ln=True, align='C')
        
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Performance Metrics:', ln=True)
        
        pdf.set_font('Arial', '', 10)
        for key, value in metrics.items():
            pdf.cell(0, 8, f'{key}: {value}', ln=True)
        
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'Total Trades: {len(trades_df)}', ln=True)
        
        return pdf.output(dest='S').encode('latin-1')
