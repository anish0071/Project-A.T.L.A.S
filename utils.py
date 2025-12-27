import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats


class RiskMetrics:
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, rf_rate: float = 0.04) -> float:
        annual_ret = returns.mean() * 252
        annual_vol = returns.std() * np.sqrt(252)
        return (annual_ret - rf_rate) / annual_vol if annual_vol != 0 else 0
    
    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, rf_rate: float = 0.04) -> float:
        annual_ret = returns.mean() * 252
        downside = returns[returns < 0]
        downside_vol = downside.std() * np.sqrt(252)
        return (annual_ret - rf_rate) / downside_vol if downside_vol != 0 else 0
    
    @staticmethod
    def calculate_calmar_ratio(returns: pd.Series, equity: pd.Series) -> float:
        annual_ret = returns.mean() * 252
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max
        max_dd = drawdown.min()
        return annual_ret / abs(max_dd) if max_dd != 0 else 0
    
    @staticmethod
    def calculate_var(returns: pd.Series, confidence: float = 0.95) -> float:
        return np.percentile(returns, (1 - confidence) * 100)
    
    @staticmethod
    def calculate_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
        var = np.percentile(returns, (1 - confidence) * 100)
        return returns[returns <= var].mean()
    
    @staticmethod
    def calculate_win_rate(returns: pd.Series) -> float:
        wins = (returns > 0).sum()
        total = (returns != 0).sum()
        return wins / total if total > 0 else 0
    
    @staticmethod
    def calculate_profit_factor(returns: pd.Series) -> float:
        profits = returns[returns > 0].sum()
        losses = abs(returns[returns < 0].sum())
        return profits / losses if losses != 0 else 0


class Formatter:
    
    @staticmethod
    def format_currency(value: float, precision: int = 2) -> str:
        return f"₹{value:,.{precision}f}"
    
    @staticmethod
    def format_percentage(value: float, precision: int = 2) -> str:
        return f"{value * 100:.{precision}f}%"
    
    @staticmethod
    def format_ratio(value: float, precision: int = 2) -> str:
        return f"{value:.{precision}f}"
    
    @staticmethod
    def format_number(value: float, precision: int = 2) -> str:
        return f"{value:,.{precision}f}"


class DateHelper:
    
    @staticmethod
    def get_period_options() -> Dict[str, str]:
        return {
            '1mo': '1 Month',
            '3mo': '3 Months',
            '6mo': '6 Months',
            '1y': '1 Year',
            '2y': '2 Years',
            '5y': '5 Years',
            'max': 'Max',
        }
