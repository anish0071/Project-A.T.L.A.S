import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class DataFetcher:
    NSE_TICKERS = {
        'SBIN': 'SBIN.NS',
        'INFY': 'INFY.NS',
        'TCS': 'TCS.NS',
        'HDFC': 'HDFC.NS',
        'RELIANCE': 'RELIANCE.NS',
        'BAJAJ-AUTO': 'BAJAJAUT.NS',
        'ITC': 'ITC.NS',
        'MARUTI': 'MARUTI.NS',
        'AXIS': 'AXISBANK.NS',
        'LT': 'LT.NS',
        'NIFTY50': '^NSEI',
    }
    
    def __init__(self):
        self.cache = {}
    
    @staticmethod
    def fetch_historical_data(ticker: str, period: str = '5y', interval: str = '1d') -> pd.DataFrame:
        try:
            ticker_key = DataFetcher.NSE_TICKERS.get(ticker, ticker)
            data = yf.download(ticker_key, period=period, interval=interval, progress=False)
            if data.empty:
                return pd.DataFrame()
            data = data[['Close']].dropna()
            data.columns = ['close']
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def fetch_intraday_data(ticker: str, days: int = 30) -> pd.DataFrame:
        try:
            ticker_key = DataFetcher.NSE_TICKERS.get(ticker, ticker)
            data = yf.download(ticker_key, period=f'{days}d', interval='1h', progress=False)
            return data[['Close']].dropna() if not data.empty else pd.DataFrame()
        except:
            return pd.DataFrame()
    
    @staticmethod
    def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        prices = df['close'] if 'close' in df.columns else df.iloc[:, 0]
        
        df['sma_20'] = prices.rolling(20).mean()
        df['sma_50'] = prices.rolling(50).mean()
        df['ema_12'] = prices.ewm(span=12).mean()
        df['ema_26'] = prices.ewm(span=26).mean()
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        df['std_20'] = prices.rolling(20).std()
        df['bb_upper'] = df['sma_20'] + (df['std_20'] * 2)
        df['bb_lower'] = df['sma_20'] - (df['std_20'] * 2)
        
        df['momentum_10'] = prices.pct_change(10)
        df['roc'] = ((prices - prices.shift(12)) / prices.shift(12)) * 100
        
        return df
    
    @staticmethod
    def get_available_tickers() -> List[str]:
        return list(DataFetcher.NSE_TICKERS.keys())
