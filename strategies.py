import pandas as pd
import numpy as np
from typing import Tuple, Dict


class TradingStrategies:
    
    @staticmethod
    def sma_crossover(prices: pd.Series, short_window: int = 20, long_window: int = 50) -> pd.Series:
        sma_short = prices.rolling(window=short_window).mean()
        sma_long = prices.rolling(window=long_window).mean()
        signals = pd.Series(0, index=prices.index)
        signals[sma_short > sma_long] = 1
        return signals
    
    @staticmethod
    def ema_crossover(prices: pd.Series, short_window: int = 12, long_window: int = 26) -> pd.Series:
        ema_short = prices.ewm(span=short_window).mean()
        ema_long = prices.ewm(span=long_window).mean()
        signals = pd.Series(0, index=prices.index)
        signals[ema_short > ema_long] = 1
        return signals
    
    @staticmethod
    def rsi_strategy(prices: pd.Series, period: int = 14, oversold: int = 30, overbought: int = 70) -> pd.Series:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        signals = pd.Series(0, index=prices.index)
        signals[rsi < oversold] = 1
        signals[rsi > overbought] = 0
        return signals
    
    @staticmethod
    def macd_strategy(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        signals = pd.Series(0, index=prices.index)
        signals[macd > signal_line] = 1
        return signals
    
    @staticmethod
    def bollinger_bands(prices: pd.Series, period: int = 20, num_std: float = 2.0) -> pd.Series:
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        lower_band = sma - (num_std * std)
        upper_band = sma + (num_std * std)
        signals = pd.Series(0, index=prices.index)
        signals[prices < lower_band] = 1
        signals[prices > upper_band] = 0
        return signals
    
    @staticmethod
    def stochastic_oscillator(prices: pd.Series, period: int = 14, smooth: int = 3) -> pd.Series:
        low_min = prices.rolling(window=period).min()
        high_max = prices.rolling(window=period).max()
        k = 100 * (prices - low_min) / (high_max - low_min)
        k_smooth = k.rolling(window=smooth).mean()
        signals = pd.Series(0, index=prices.index)
        signals[k_smooth < 20] = 1
        signals[k_smooth > 80] = 0
        return signals
    
    @staticmethod
    def momentum(prices: pd.Series, period: int = 10) -> pd.Series:
        momentum = prices.pct_change(period)
        signals = pd.Series(0, index=prices.index)
        signals[momentum > 0] = 1
        return signals
    
    @staticmethod
    def roc_strategy(prices: pd.Series, period: int = 12) -> pd.Series:
        roc = ((prices - prices.shift(period)) / prices.shift(period)) * 100
        signals = pd.Series(0, index=prices.index)
        signals[roc > 0] = 1
        return signals
    
    @staticmethod
    def atr_breakout(prices: pd.Series, period: int = 14, multiplier: float = 2.0) -> pd.Series:
        high = prices
        low = prices * 0.98
        close = prices
        tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
        atr = pd.Series(tr).rolling(window=period).mean()
        signals = pd.Series(0, index=prices.index)
        upper = close + (multiplier * atr)
        signals[close > upper.shift(1)] = 1
        return signals
    
    @staticmethod
    def volume_weighted_ma(prices: pd.Series, period: int = 20) -> pd.Series:
        sma = prices.rolling(window=period).mean()
        signals = pd.Series(0, index=prices.index)
        signals[prices > sma] = 1
        return signals
    
    @staticmethod
    def support_resistance(prices: pd.Series, period: int = 50) -> pd.Series:
        rolling_high = prices.rolling(window=period).max()
        rolling_low = prices.rolling(window=period).min()
        signals = pd.Series(0, index=prices.index)
        signals[(prices > rolling_low) & (prices < rolling_high)] = 1
        return signals
    
    @staticmethod
    def trend_following(prices: pd.Series, threshold: float = 0.02) -> pd.Series:
        returns = prices.pct_change()
        signals = pd.Series(0, index=prices.index)
        signals[returns > threshold] = 1
        signals[returns < -threshold] = 0
        return signals
    
    @staticmethod
    def mean_reversion(prices: pd.Series, period: int = 20, threshold: float = 1.5) -> pd.Series:
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        signals = pd.Series(0, index=prices.index)
        signals[prices < (sma - threshold * std)] = 1
        signals[prices > (sma + threshold * std)] = 0
        return signals
    
    @staticmethod
    def williams_r(prices: pd.Series, period: int = 14) -> pd.Series:
        high = prices.rolling(window=period).max()
        low = prices.rolling(window=period).min()
        wr = -100 * (high - prices) / (high - low)
        signals = pd.Series(0, index=prices.index)
        signals[wr < -80] = 1
        signals[wr > -20] = 0
        return signals
    
    @staticmethod
    def adx_trend(prices: pd.Series, period: int = 14) -> pd.Series:
        returns = prices.pct_change()
        trend = returns.rolling(window=period).std()
        signals = pd.Series(0, index=prices.index)
        signals[trend > trend.mean()] = 1
        return signals
    
    @staticmethod
    def fibonacci_retracement(prices: pd.Series, period: int = 50) -> pd.Series:
        high = prices.rolling(window=period).max()
        low = prices.rolling(window=period).min()
        fib_38 = low + 0.382 * (high - low)
        signals = pd.Series(0, index=prices.index)
        signals[prices < fib_38] = 1
        return signals
    
    @staticmethod
    def ichimoku_cloud(prices: pd.Series, period1: int = 9, period2: int = 26) -> pd.Series:
        high_9 = prices.rolling(window=period1).max()
        low_9 = prices.rolling(window=period1).min()
        tenkan = (high_9 + low_9) / 2
        high_26 = prices.rolling(window=period2).max()
        low_26 = prices.rolling(window=period2).min()
        kijun = (high_26 + low_26) / 2
        signals = pd.Series(0, index=prices.index)
        signals[tenkan > kijun] = 1
        return signals


def get_strategy(name: str) -> callable:
    strategies = {
        'SMA Crossover': TradingStrategies.sma_crossover,
        'EMA Crossover': TradingStrategies.ema_crossover,
        'RSI': TradingStrategies.rsi_strategy,
        'MACD': TradingStrategies.macd_strategy,
        'Bollinger Bands': TradingStrategies.bollinger_bands,
        'Stochastic': TradingStrategies.stochastic_oscillator,
        'Momentum': TradingStrategies.momentum,
        'ROC': TradingStrategies.roc_strategy,
        'ATR Breakout': TradingStrategies.atr_breakout,
        'Volume MA': TradingStrategies.volume_weighted_ma,
        'Support/Resistance': TradingStrategies.support_resistance,
        'Trend Following': TradingStrategies.trend_following,
        'Mean Reversion': TradingStrategies.mean_reversion,
        'Williams %R': TradingStrategies.williams_r,
        'ADX Trend': TradingStrategies.adx_trend,
        'Fibonacci': TradingStrategies.fibonacci_retracement,
        'Ichimoku Cloud': TradingStrategies.ichimoku_cloud,
    }
    return strategies.get(name, TradingStrategies.sma_crossover)


STRATEGY_CONFIGS = {
    'SMA Crossover': {'short_window': (5, 50), 'long_window': (20, 200)},
    'EMA Crossover': {'short_window': (5, 50), 'long_window': (20, 200)},
    'RSI': {'period': (5, 50), 'oversold': (10, 50), 'overbought': (50, 90)},
    'MACD': {'fast': (5, 20), 'slow': (20, 50), 'signal': (5, 20)},
    'Bollinger Bands': {'period': (10, 50), 'num_std': (1.0, 3.0)},
    'Stochastic': {'period': (5, 30), 'smooth': (1, 5)},
    'Momentum': {'period': (5, 50)},
    'ROC': {'period': (5, 50)},
    'ATR Breakout': {'period': (10, 50), 'multiplier': (1.0, 3.0)},
    'Mean Reversion': {'period': (10, 50), 'threshold': (0.5, 2.5)},
}
