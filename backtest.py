"""
Backtesting Engine - Simplified version without VectorBT (Mac M1/M2 compatible)
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


@dataclass
class BacktestConfig:
    initial_cash: float = 100000
    brokerage_fee: float = 0.001
    stt_tax: float = 0.001
    slippage: float = 0.0002
    max_trades: int = 1000
    

class QuantBacktester:
    def __init__(self, config: BacktestConfig = None):
        self.config = config or BacktestConfig()
        self.results = None
        self.stats = None
        
    def calculate_returns(self, price_series: pd.Series) -> pd.Series:
        return price_series.pct_change().fillna(0)
    
    def calculate_sharp_ratio(self, returns: pd.Series, rf_rate: float = 0.04) -> float:
        if len(returns) == 0:
            return 0.0
        annual_ret = returns.mean() * 252
        annual_vol = returns.std() * np.sqrt(252)
        if annual_vol == 0:
            return 0.0
        return (annual_ret - rf_rate) / annual_vol
    
    def calculate_sortino_ratio(self, returns: pd.Series, rf_rate: float = 0.04) -> float:
        if len(returns) == 0:
            return 0.0
        annual_ret = returns.mean() * 252
        downside_ret = returns[returns < 0]
        downside_vol = downside_ret.std() * np.sqrt(252)
        if downside_vol == 0:
            return 0.0
        return (annual_ret - rf_rate) / downside_vol
    
    def calculate_max_drawdown(self, equity_curve: pd.Series) -> Tuple[float, str]:
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max
        max_dd = drawdown.min()
        max_dd_date = drawdown.idxmin()
        return max_dd, max_dd_date
    
    def calculate_calmar_ratio(self, returns: pd.Series, equity_curve: pd.Series) -> float:
        max_dd, _ = self.calculate_max_drawdown(equity_curve)
        if max_dd == 0:
            return 0.0
        annual_ret = returns.mean() * 252
        return annual_ret / abs(max_dd)
    
    def calculate_var(self, returns: pd.Series, confidence: float = 0.95) -> float:
        return np.percentile(returns, (1 - confidence) * 100)
    
    def backtest_strategy(self, prices: pd.Series, signals: pd.Series, strategy_name: str = "Strategy") -> Dict:
        """Backtest a strategy"""
        returns = self.calculate_returns(prices)
        
        # Fill forward positions
        positions = signals.copy()
        positions = positions.fillna(method='ffill').fillna(0)
        
        # Calculate strategy returns
        strategy_returns = positions.shift(1) * returns
        
        # Calculate costs
        cost_series = abs(positions.diff()).fillna(0) * self.config.brokerage_fee
        cost_series += (positions.diff() < 0).fillna(False) * 0.001 * self.config.stt_tax
        
        # Net returns after costs
        net_returns = strategy_returns - cost_series
        equity_curve = (1 + net_returns).cumprod() * self.config.initial_cash
        
        total_return = (equity_curve.iloc[-1] / self.config.initial_cash - 1)
        max_dd, max_dd_date = self.calculate_max_drawdown(equity_curve)
        annual_ret = returns.mean() * 252
        annual_vol = returns.std() * np.sqrt(252)
        
        wins = (net_returns > 0).sum()
        total_trades = (net_returns != 0).sum()
        win_rate = wins / total_trades if total_trades > 0 else 0
        
        return {
            'strategy_name': strategy_name,
            'equity_curve': equity_curve,
            'returns': net_returns,
            'positions': positions,
            'total_return': total_return,
            'annual_return': annual_ret,
            'annual_volatility': annual_vol,
            'sharpe_ratio': self.calculate_sharp_ratio(net_returns),
            'sortino_ratio': self.calculate_sortino_ratio(net_returns),
            'calmar_ratio': self.calculate_calmar_ratio(net_returns, equity_curve),
            'max_drawdown': max_dd,
            'max_drawdown_date': max_dd_date,
            'var_95': self.calculate_var(net_returns, 0.95),
            'win_rate': win_rate,
            'total_trades': total_trades,
        }
