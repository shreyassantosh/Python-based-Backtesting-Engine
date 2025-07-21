import pandas as pd
import numpy as np

# Data fetching
import yfinance as yf
from main_backtesting_engine import BacktestingEngine


# Date and time handling
from datetime import datetime, timedelta

# Visualization
import plotly.graph_objects as go
import plotly.subplots as sp
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit for web interface
import streamlit as st

# System and utility
import warnings
warnings.filterwarnings('ignore')

# For statistical calculations (if needed)
from scipy import stats

# For additional analysis (optional)
from sklearn.metrics import mean_squared_error
def create_dashboard():
    """Create Streamlit dashboard interface"""
    st.set_page_config(page_title="Trading Strategy Backtester", layout="wide")
    
    st.title("🚀 Technical Trading Strategy Backtester")
    st.markdown("---")
    
    # Sidebar for inputs
    st.sidebar.header("Strategy Parameters")
    
    # Basic inputs
    ticker = st.sidebar.text_input("Stock Ticker", value="AAPL")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    initial_capital = st.sidebar.number_input("Initial Capital", value=100000, min_value=1000)
    
    # Technical indicator settings
    st.sidebar.subheader("Technical Indicators")
    
    use_rsi = st.sidebar.checkbox("Use RSI", value=True)
    if use_rsi:
        rsi_buy = st.sidebar.slider("RSI Buy Threshold", 0, 100, 30)
        rsi_sell = st.sidebar.slider("RSI Sell Threshold", 0, 100, 70)
    else:
        rsi_buy = rsi_sell = 0
    
    use_macd = st.sidebar.checkbox("Use MACD", value=True)
    use_ma = st.sidebar.checkbox("Use Moving Average", value=False)
    
    logic = st.sidebar.selectbox("Strategy Logic", ["AND", "OR"])
    
    # Run backtest button
    if st.sidebar.button("🎯 Run Backtest"):
        strategy_params = {
            'use_rsi': use_rsi,
            'rsi_buy_threshold': rsi_buy,
            'rsi_sell_threshold': rsi_sell,
            'use_macd': use_macd,
            'use_ma': use_ma,
            'logic': logic
        }
        
        # Initialize and run backtest
        engine = BacktestingEngine(ticker, start_date, end_date, initial_capital)
        
        with st.spinner("Fetching data and running backtest..."):
            if engine.fetch_data() and engine.calculate_indicators():
                engine.generate_signals(strategy_params)
                engine.simulate_trading()
                
                # Display results
                display_results(engine)
            else:
                st.error("Failed to fetch data or calculate indicators")

def display_results(engine):
    """Display backtest results"""
    
    # Performance metrics
    metrics = engine.calculate_performance_metrics()
    
    st.header("📊 Performance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cumulative Return", f"{metrics['Cumulative Return (%)']}%")
        st.metric("Sharpe Ratio", metrics['Sharpe Ratio'])
    
    with col2:
        st.metric("Max Drawdown", f"{metrics['Max Drawdown (%)']}%")
        st.metric("Win/Loss Ratio", metrics['Win/Loss Ratio'])
    
    with col3:
        st.metric("Total Trades", metrics['Total Trades'])
        st.metric("Volatility", f"{metrics['Volatility (%)']}%")
    
    with col4:
        st.metric("Final Value", f"${metrics['Final Portfolio Value']:,.0f}")
        initial_value = engine.initial_capital
        st.metric("Profit/Loss", f"${metrics['Final Portfolio Value'] - initial_value:,.0f}")
    
    # Create interactive charts
    create_interactive_charts(engine)
    
    # Trade log
    display_trade_log(engine)
    
    # Export options
    create_export_options(engine, metrics)

def create_interactive_charts(engine):
    """Create interactive Plotly charts"""
    
    st.header("📈 Interactive Charts")
    
    # Create subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('Price & Signals', 'Portfolio Value', 'RSI', 'MACD'),
        row_heights=[0.4, 0.2, 0.2, 0.2]
    )
    
    # Price chart with buy/sell signals
    fig.add_trace(
        go.Scatter(x=engine.data.index, y=engine.data['Close'], 
                  name='Close Price', line=dict(color='blue')),
        row=1, col=1
    )
    
    # Buy signals
    buy_signals = engine.data[engine.data['Signal'] == 1]
    if not buy_signals.empty:
        fig.add_trace(
            go.Scatter(x=buy_signals.index, y=buy_signals['Close'],
                      mode='markers', name='Buy Signal',
                      marker=dict(color='green', size=10, symbol='triangle-up')),
            row=1, col=1
        )
    
    # Sell signals
    sell_signals = engine.data[engine.data['Signal'] == -1]
    if not sell_signals.empty:
        fig.add_trace(
            go.Scatter(x=sell_signals.index, y=sell_signals['Close'],
                      mode='markers', name='Sell Signal',
                      marker=dict(color='red', size=10, symbol='triangle-down')),
            row=1, col=1
        )
    
    # Portfolio value
    fig.add_trace(
        go.Scatter(x=engine.data.index, y=engine.data['Portfolio_Value'],
                  name='Portfolio Value', line=dict(color='purple')),
        row=2, col=1
    )
    
    # RSI
    fig.add_trace(
        go.Scatter(x=engine.data.index, y=engine.data['RSI'],
                  name='RSI', line=dict(color='orange')),
        row=3, col=1
    )
    
    # RSI overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # MACD
    fig.add_trace(
        go.Scatter(x=engine.data.index, y=engine.data['MACD'],
                  name='MACD', line=dict(color='blue')),
        row=4, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=engine.data.index, y=engine.data['MACD_Signal'],
                  name='MACD Signal', line=dict(color='red')),
        row=4, col=1
    )
    
    # Update layout
    fig.update_layout(
        title=f"{engine.ticker} Trading Strategy Backtest Results",
        height=800,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_trade_log(engine):
    """Display trade log table"""
    
    st.header("📋 Trade Log")
    
    if engine.trades:
        trades_df = pd.DataFrame(engine.trades)
        trades_df['Date'] = pd.to_datetime(trades_df['Date']).dt.strftime('%Y-%m-%d')
        st.dataframe(trades_df, use_container_width=True)
    else:
        st.info("No trades executed with current strategy parameters")

def create_export_options(engine, metrics):
    """Create export functionality"""
    
    st.header("📤 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Download Performance Report (CSV)"):
            # Create performance summary
            performance_df = pd.DataFrame([metrics])
            csv_data = performance_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"{engine.ticker}_performance_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Download Trade Log (CSV)"):
            if engine.trades:
                trades_df = pd.DataFrame(engine.trades)
                csv_data = trades_df.to_csv(index=False)
                st.download_button(
                    label="Download Trade Log",
                    data=csv_data,
                    file_name=f"{engine.ticker}_trades_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No trades to export")

# Run the dashboard
if __name__ == "__main__":
    create_dashboard()
