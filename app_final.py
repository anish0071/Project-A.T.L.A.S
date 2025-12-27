import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from backtest import QuantBacktester, BacktestConfig
from strategies import get_strategy, STRATEGY_CONFIGS
from data import DataFetcher
from utils import RiskMetrics, Formatter

st.set_page_config(
    page_title="Quant Backtester - Professional Trading Engine",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Professional Algorithmic Trading Platform"}
)

# Professional Black & Green Theme with Bold Typography
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Professional Black Backdrop */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Sidebar - Professional Black with Green Accent */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 3px solid #00ff41 !important;
        box-shadow: 0 0 40px rgba(0, 255, 65, 0.1) !important;
    }
    
    [data-testid="stSidebar"] > div {
        background-color: transparent !important;
    }
    
    /* Main Content */
    .main {
        background-color: #000000 !important;
    }
    
    /* Headers - Bold & Visible */
    h1 {
        color: #00ff41 !important;
        font-weight: 900 !important;
        font-size: 3.5rem !important;
        letter-spacing: -2px !important;
        line-height: 1.1 !important;
        text-shadow: 0 0 30px rgba(0, 255, 65, 0.2) !important;
        margin-bottom: 15px !important;
    }
    
    h2 {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        letter-spacing: -0.5px !important;
        margin-top: 40px !important;
        margin-bottom: 20px !important;
    }
    
    h3 {
        color: #00ff41 !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-top: 20px !important;
        margin-bottom: 15px !important;
    }
    
    h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Paragraph & Text - Bold & Visible */
    p, label, span, div {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }
    
    /* Input Labels - BOLD, BIG, VISIBLE */
    [data-testid="stNumberInput"] label,
    [data-testid="stSelectbox"] label,
    [data-testid="stSlider"] label {
        color: #00ff41 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        margin-bottom: 12px !important;
        display: block !important;
    }
    
    /* Input Fields - Professional Black with Green Border */
    .stNumberInput input,
    .stSelectbox select,
    .stTextInput input,
    input[type="number"],
    input[type="text"],
    select {
        background-color: #1a1a1a !important;
        color: #00ff41 !important;
        border: 2px solid #00ff41 !important;
        border-radius: 8px !important;
        padding: 14px 18px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 0 15px rgba(0, 255, 65, 0.05) !important;
    }
    
    input[type="number"]:focus,
    input[type="text"]:focus,
    select:focus {
        border-color: #00ff41 !important;
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.4), inset 0 0 10px rgba(0, 255, 65, 0.1) !important;
        background-color: #1a1a1a !important;
        outline: none !important;
    }
    
    /* Slider - Professional Green */
    .stSlider [data-testid="stTickBar"] {
        background: linear-gradient(90deg, #00ff41 0%, #00dd38 100%) !important;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3) !important;
    }
    
    .stSlider > div > div > div > div {
        background-color: #00ff41 !important;
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.5) !important;
    }
    
    /* Buttons - Bold Green, Professional */
    .stButton > button {
        background: linear-gradient(135deg, #00ff41 0%, #00dd38 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 16px 40px !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.3) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00dd38 0%, #00ff41 100%) !important;
        box-shadow: 0 0 50px rgba(0, 255, 65, 0.5) !important;
        transform: translateY(-3px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00ff41 0%, #00dd38 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 14px 32px !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 0 50px rgba(0, 255, 65, 0.5) !important;
        transform: translateY(-3px) !important;
    }
    
    /* Metric Cards - Bold Text, Clear Values */
    .stMetric {
        background-color: #1a1a1a !important;
        border: 2px solid #00ff41 !important;
        border-radius: 8px !important;
        padding: 28px !important;
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stMetric:hover {
        border-color: #00ff41 !important;
        box-shadow: 0 0 40px rgba(0, 255, 65, 0.2) !important;
        transform: translateY(-4px) !important;
    }
    
    .stMetric [data-testid="stMetricLabel"] {
        color: #00ff41 !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #00ff41 !important;
        font-weight: 900 !important;
        font-size: 2.5rem !important;
        text-shadow: 0 0 20px rgba(0, 255, 65, 0.2) !important;
    }
    
    /* Tabs - Professional Style */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #00ff41 !important;
        gap: 40px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        background-color: transparent !important;
        color: #888888 !important;
        border-bottom: 3px solid transparent !important;
        padding: 16px 8px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover {
        color: #00ff41 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: transparent !important;
        color: #00ff41 !important;
        border-bottom: 3px solid #00ff41 !important;
        box-shadow: 0 -8px 25px rgba(0, 255, 65, 0.2) !important;
    }
    
    /* Tables - Professional, Bold Headers */
    table {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
    }
    
    tbody tr {
        border-bottom: 1px solid #00ff41 !important;
        transition: all 0.3s ease !important;
    }
    
    tbody tr:hover {
        background-color: #1a1a1a !important;
    }
    
    thead th {
        background-color: #1a1a1a !important;
        color: #00ff41 !important;
        border-bottom: 2px solid #00ff41 !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        padding: 16px !important;
        font-size: 1rem !important;
    }
    
    /* Scrollbar - Professional */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00ff41, #00dd38);
        border-radius: 6px;
        border: 2px solid #0a0a0a;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00dd38, #00ff41);
    }
    </style>
""", unsafe_allow_html=True)

# Professional Header
st.markdown("""
    <div style='
        text-align: center; 
        padding: 60px 40px 50px 40px; 
        margin-bottom: 50px;
        background-color: #1a1a1a;
        border-bottom: 3px solid #00ff41;
        border-radius: 12px;
    '>
        <h1 style='margin-bottom: 10px;'>QUANT BACKTESTER</h1>
        <p style='color: #00ff41; font-size: 1.3rem; letter-spacing: 2px; text-transform: uppercase; font-weight: 800;'>
            Professional Algorithmic Trading Engine
        </p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("""
        <h3 style='color: #00ff41; margin-bottom: 30px;'>Configuration</h3>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='color: #00ff41; font-weight: 800; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px;'>Stock Ticker</p>", unsafe_allow_html=True)
    ticker = st.selectbox("Ticker", DataFetcher.get_available_tickers(), label_visibility="collapsed")
    
    st.markdown("<p style='color: #00ff41; font-weight: 800; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 20px;'>Historical Period</p>", unsafe_allow_html=True)
    period = st.select_slider("Period", options=['1mo', '3mo', '6mo', '1y', '2y', '5y'], value='5y', label_visibility="collapsed")
    
    st.markdown("<p style='color: #00ff41; font-weight: 800; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 20px;'>Trading Strategy</p>", unsafe_allow_html=True)
    strategy_name = st.selectbox("Strategy", list(STRATEGY_CONFIGS.keys()), label_visibility="collapsed")
    
    st.markdown("<p style='color: #00ff41; font-weight: 800; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 20px;'>Initial Capital (₹)</p>", unsafe_allow_html=True)
    initial_capital = st.number_input("Capital", value=100000, min_value=10000, step=10000, label_visibility="collapsed")
    
    st.markdown("""
        <div style='margin-top: 40px; padding-top: 30px; border-top: 2px solid #00ff41;'>
            <h3 style='color: #00ff41; margin-bottom: 25px;'>Strategy Parameters</h3>
        </div>
    """, unsafe_allow_html=True)
    
    params = {}
    if strategy_name in STRATEGY_CONFIGS:
        for param, (min_val, max_val) in STRATEGY_CONFIGS[strategy_name].items():
            st.markdown(f"<p style='color: #00ff41; font-weight: 800; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 15px;'>{param}</p>", unsafe_allow_html=True)
            if isinstance(min_val, int):
                params[param] = st.slider(
                    param, 
                    min_value=int(min_val), 
                    max_value=int(max_val), 
                    value=int((min_val + max_val) / 2),
                    label_visibility="collapsed"
                )
            else:
                params[param] = st.slider(
                    param, 
                    min_value=min_val, 
                    max_value=max_val, 
                    value=(min_val + max_val) / 2, 
                    step=0.1,
                    label_visibility="collapsed"
                )
    
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    run_button = st.button("RUN BACKTEST", use_container_width=True, key="run_bt")

if run_button:
    with st.spinner("🔄 Analyzing market data..."):
        data = DataFetcher.fetch_historical_data(ticker, period=period)
        
        if data.empty:
            st.error("❌ Could not fetch data for selected ticker")
        else:
            prices = data['close']
            strategy_func = get_strategy(strategy_name)
            signals = strategy_func(prices, **params)
            backtester = QuantBacktester(BacktestConfig(initial_cash=initial_capital))
            results = backtester.backtest_strategy(prices, signals, strategy_name)
            
            # Results Section
            st.markdown("""
                <div style='padding: 30px 0; margin-bottom: 40px; border-bottom: 2px solid #00ff41;'>
                    <h2 style='margin-top: 0;'>PERFORMANCE METRICS</h2>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns(5, gap="medium")
            
            with col1:
                st.metric("Total Return", Formatter.format_percentage(results['total_return']))
            with col2:
                st.metric("Sharpe Ratio", Formatter.format_ratio(results['sharpe_ratio']))
            with col3:
                st.metric("Max Drawdown", Formatter.format_percentage(results['max_drawdown']))
            with col4:
                st.metric("Win Rate", Formatter.format_percentage(results['win_rate']))
            with col5:
                st.metric("Volatility", Formatter.format_percentage(results['annual_volatility']))
            
            st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
            
            # Charts Section
            st.markdown("""
                <div style='padding: 0 0 20px 0; margin-bottom: 30px;'>
                    <h2 style='margin-top: 0;'>DETAILED ANALYSIS</h2>
                </div>
            """, unsafe_allow_html=True)
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Equity Curve", "Drawdown", "Returns Distribution", "Price Action", "Metrics"])
            
            with tab1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=results['equity_curve'].values, 
                    mode='lines', 
                    name='Portfolio Value',
                    line=dict(color='#00ff41', width=4),
                    fill='tozeroy',
                    fillcolor='rgba(0, 255, 65, 0.15)',
                    hovertemplate='<b>Value: ₹%{y:,.0f}</b><extra></extra>'
                ))
                fig.update_layout(
                    title="Portfolio Growth Over Time",
                    xaxis_title="Days",
                    yaxis_title="Portfolio Value (₹)",
                    template="plotly_dark",
                    hovermode='x unified',
                    plot_bgcolor='#0a0a0a',
                    paper_bgcolor='#000000',
                    font=dict(color='#ffffff', size=14, family='Inter'),
                    margin=dict(l=80, r=40, t=80, b=60),
                    title_font_size=20,
                    title_font_color='#00ff41',
                    xaxis_tickfont=dict(size=12),
                    yaxis_tickfont=dict(size=12)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})
            
            with tab2:
                running_max = results['equity_curve'].expanding().max()
                drawdown = (results['equity_curve'] - running_max) / running_max * 100
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=drawdown.values, 
                    fill='tozeroy', 
                    name='Drawdown',
                    line=dict(color='#ff0000', width=3),
                    fillcolor='rgba(255, 0, 0, 0.2)',
                    hovertemplate='<b>Drawdown: %{y:.2f}%</b><extra></extra>'
                ))
                fig.update_layout(
                    title="Drawdown Analysis",
                    xaxis_title="Days",
                    yaxis_title="Drawdown %",
                    template="plotly_dark",
                    hovermode='x unified',
                    plot_bgcolor='#0a0a0a',
                    paper_bgcolor='#000000',
                    font=dict(color='#ffffff', size=14, family='Inter'),
                    margin=dict(l=80, r=40, t=80, b=60),
                    title_font_size=20,
                    title_font_color='#00ff41',
                    xaxis_tickfont=dict(size=12),
                    yaxis_tickfont=dict(size=12)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})
            
            with tab3:
                fig = px.histogram(
                    x=results['returns'].values, 
                    nbins=50, 
                    title="Daily Returns Distribution",
                    labels={'x': 'Daily Returns (%)', 'count': 'Frequency'}
                )
                fig.update_traces(marker_color='#00ff41', marker_line_width=0)
                fig.update_layout(
                    template="plotly_dark",
                    plot_bgcolor='#0a0a0a',
                    paper_bgcolor='#000000',
                    font=dict(color='#ffffff', size=14, family='Inter'),
                    margin=dict(l=80, r=40, t=80, b=60),
                    title_font_size=20,
                    title_font_color='#00ff41',
                    xaxis_tickfont=dict(size=12),
                    yaxis_tickfont=dict(size=12)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})
            
            with tab4:
                df_prices = data.copy()
                df_prices['Open'] = df_prices['close'].shift(1)
                df_prices['High'] = df_prices['close'].rolling(window=5).max()
                df_prices['Low'] = df_prices['close'].rolling(window=5).min()
                df_prices = df_prices.dropna()
                
                fig = go.Figure(data=[go.Candlestick(
                    x=df_prices.index,
                    open=df_prices['Open'],
                    high=df_prices['High'],
                    low=df_prices['Low'],
                    close=df_prices['close'],
                    increasing_line_color='#00ff41',
                    decreasing_line_color='#ff0000',
                    increasing_fillcolor='rgba(0, 255, 65, 0.4)',
                    decreasing_fillcolor='rgba(255, 0, 0, 0.4)',
                    name='Price'
                )])
                fig.update_layout(
                    title="Interactive Candlestick Chart - Pan & Zoom Enabled",
                    xaxis_title="Date",
                    yaxis_title="Price (₹)",
                    template="plotly_dark",
                    hovermode='x unified',
                    plot_bgcolor='#0a0a0a',
                    paper_bgcolor='#000000',
                    font=dict(color='#ffffff', size=14, family='Inter'),
                    margin=dict(l=80, r=40, t=80, b=60),
                    title_font_size=20,
                    title_font_color='#00ff41',
                    xaxis_tickfont=dict(size=12),
                    yaxis_tickfont=dict(size=12),
                    height=700
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'toImageButtonOptions': {'format': 'png'}})
            
            with tab5:
                metrics_df = pd.DataFrame({
                    'Metric': ['Total Return', 'Annual Return', 'Annual Volatility', 'Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio', 'Max Drawdown', 'Win Rate', 'Total Trades', 'VaR (95%)'],
                    'Value': [
                        Formatter.format_percentage(results['total_return']),
                        Formatter.format_percentage(results['annual_return']),
                        Formatter.format_percentage(results['annual_volatility']),
                        f"{results['sharpe_ratio']:.2f}",
                        f"{results['sortino_ratio']:.2f}",
                        f"{results['calmar_ratio']:.2f}",
                        Formatter.format_percentage(results['max_drawdown']),
                        Formatter.format_percentage(results['win_rate']),
                        f"{results['total_trades']:.0f}",
                        Formatter.format_percentage(results['var_95'])
                    ]
                })
                st.dataframe(metrics_df, use_container_width=True, hide_index=True)
            
            # Export Section
            st.markdown("""
                <div style='padding-top: 50px; margin-top: 50px; border-top: 2px solid #00ff41;'>
                    <h2 style='margin-top: 0;'>EXPORT RESULTS</h2>
                </div>
            """, unsafe_allow_html=True)
            
            csv_data = results['equity_curve'].to_csv()
            st.download_button("DOWNLOAD CSV", csv_data, "backtest_results.csv", "text/csv", use_container_width=True)
