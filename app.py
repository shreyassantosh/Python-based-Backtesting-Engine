import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add project modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.fetch_data import DataFetcher
from strategies.rsi_macd_strategy import RSIMACDStrategy
from backtest.backtest_engine import BacktestEngine
from reports.metrics import PerformanceMetrics
from ui.dashboard import Dashboard

def main():
    # Initialize components
    data_fetcher = DataFetcher()
    dashboard = Dashboard()
    
    st.title("📈 Python Backtesting Engine")
    st.markdown("Evaluate technical trading strategies with historical data")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    # Stock selection
    ticker = st.sidebar.selectbox(
        "Select Stock Ticker",
        data_fetcher.get_available_tickers(),
        index=0
    )
    
    # Date range
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365),
            max_value=datetime.now()
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    # Strategy parameters
    st.sidebar.subheader("Strategy Parameters")
    
    rsi_period = st.sidebar.slider("RSI Period", 5, 30, 14)
    rsi_oversold = st.sidebar.slider("RSI Oversold", 10, 40, 30)
    rsi_overbought = st.sidebar.slider("RSI Overbought", 60, 90, 70)
    
    macd_fast = st.sidebar.slider("MACD Fast", 5, 20, 12)
    macd_slow = st.sidebar.slider("MACD Slow", 15, 40, 26)
    macd_signal = st.sidebar.slider("MACD Signal", 5, 15, 9)
    
    # Backtesting parameters
    st.sidebar.subheader("Backtesting Settings")
    initial_capital = st.sidebar.number_input("Initial Capital ($)", value=10000, min_value=1000)
    commission = st.sidebar.slider("Commission Rate (%)", 0.0, 1.0, 0.1) / 100
    
    # Run backtest button
    if st.sidebar.button("🚀 Run Backtest", type="primary"):
        
        with st.spinner("Fetching data and running backtest..."):
            try:
                # Fetch data
                data = data_fetcher.fetch_stock_data(ticker, start_date, end_date)
                
                # Initialize strategy
                strategy = RSIMACDStrategy(
                    rsi_period=rsi_period,
                    rsi_oversold=rsi_oversold,
                    rsi_overbought=rsi_overbought,
                    macd_fast=macd_fast,
                    macd_slow=macd_slow,
                    macd_signal=macd_signal
                )
                
                # Generate signals
                data_with_signals = strategy.generate_signals(data)
                
                # Run backtest
                backtest_engine = BacktestEngine(
                    initial_capital=initial_capital,
                    commission=commission
                )
                
                portfolio_df, trades_df = backtest_engine.execute_backtest(data_with_signals)
                
                # Calculate metrics
                performance = PerformanceMetrics(portfolio_df, trades_df)
                report = performance.generate_report()
                
                # Store results in session state
                st.session_state.data = data_with_signals
                st.session_state.portfolio_df = portfolio_df
                st.session_state.trades_df = trades_df
                st.session_state.report = report
                st.session_state.ticker = ticker
                
                st.success("✅ Backtest completed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display results if available
    if hasattr(st.session_state, 'report'):
        
        # Performance metrics
        st.header("📊 Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        metrics = st.session_state.report['metrics']
        
        with col1:
            st.metric("Total Return", f"{metrics['Total Return (%)']}%")
            st.metric("Sharpe Ratio", metrics['Sharpe Ratio'])
        
        with col2:
            st.metric("Max Drawdown", f"{metrics['Max Drawdown (%)']}%")
            st.metric("Volatility", f"{metrics['Volatility (%)']}%")
        
        with col3:
            st.metric("Win Rate", f"{metrics['Win Rate (%)']}%")
            st.metric("Total Trades", metrics['Total Trades'])
        
        with col4:
            st.metric("Win/Loss Ratio", metrics['Win/Loss Ratio'])
            st.metric("Avg Trade Return", f"${metrics['Avg Trade Return ($)']}")
        
        # Charts
        st.header("📈 Interactive Charts")
        
        # Price chart with signals
        price_chart = dashboard.create_price_chart(
            st.session_state.data, 
            st.session_state.trades_df
        )
        st.plotly_chart(price_chart, use_container_width=True)
        
        # Portfolio performance
        performance_chart = dashboard.create_performance_chart(
            st.session_state.portfolio_df
        )
        st.plotly_chart(performance_chart, use_container_width=True)
        
        # Trade log
        st.header("📋 Trade Log")
        if not st.session_state.trades_df.empty:
            st.dataframe(st.session_state.trades_df, use_container_width=True)
        else:
            st.info("No trades executed during the selected period.")
        
        # Export options
        st.header("📤 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV export
            csv_data = dashboard.export_to_csv(
                st.session_state.trades_df, 
                metrics
            )
            
            st.download_button(
                label="📊 Download CSV Report",
                data=csv_data,
                file_name=f"backtest_report_{st.session_state.ticker}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # PDF export
            try:
                pdf_data = dashboard.export_to_pdf(
                    metrics, 
                    st.session_state.trades_df
                )
                
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_data,
                    file_name=f"backtest_report_{st.session_state.ticker}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.warning(f"PDF export unavailable: {str(e)}")

if __name__ == "__main__":
    main()
