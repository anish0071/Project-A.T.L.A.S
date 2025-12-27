import pytest
import pandas as pd
import numpy as np
from backtest import QuantBacktester, BacktestConfig
from strategies import TradingStrategies
from utils import RiskMetrics


@pytest.fixture
def sample_price_series():
    dates = pd.date_range('2020-01-01', periods=252)
    prices = pd.Series(
        np.cumsum(np.random.randn(252)) + 100,
        index=dates
    )
    return prices


@pytest.fixture
def sample_signals(sample_price_series):
    return pd.Series(
        np.random.choice([0, 1], size=len(sample_price_series)),
        index=sample_price_series.index
    )


class TestQuantBacktester:
    def test_backtest_creation(self):
        config = BacktestConfig()
        backtester = QuantBacktester(config)
        assert backtester.config.initial_cash == 100000
    
    def test_calculate_returns(self, sample_price_series):
        backtester = QuantBacktester()
        returns = backtester.calculate_returns(sample_price_series)
        assert len(returns) == len(sample_price_series)
        assert returns.iloc[0] == 0
    
    def test_sharpe_ratio(self, sample_price_series):
        backtester = QuantBacktester()
        returns = backtester.calculate_returns(sample_price_series)
        sharpe = backtester.calculate_sharp_ratio(returns)
        assert isinstance(sharpe, float)
    
    def test_sortino_ratio(self, sample_price_series):
        backtester = QuantBacktester()
        returns = backtester.calculate_returns(sample_price_series)
        sortino = backtester.calculate_sortino_ratio(returns)
        assert isinstance(sortino, float)
    
    def test_max_drawdown(self, sample_price_series):
        backtester = QuantBacktester()
        max_dd, date = backtester.calculate_max_drawdown(sample_price_series)
        assert max_dd <= 0
        assert isinstance(date, pd.Timestamp)
    
    def test_calmar_ratio(self, sample_price_series):
        backtester = QuantBacktester()
        returns = backtester.calculate_returns(sample_price_series)
        calmar = backtester.calculate_calmar_ratio(returns, sample_price_series)
        assert isinstance(calmar, float)
    
    def test_var_calculation(self, sample_price_series):
        backtester = QuantBacktester()
        returns = backtester.calculate_returns(sample_price_series)
        var = backtester.calculate_var(returns)
        assert isinstance(var, (int, float))
    
    def test_backtest_strategy(self, sample_price_series, sample_signals):
        backtester = QuantBacktester()
        results = backtester.backtest_strategy(sample_price_series, sample_signals)
        assert 'sharpe_ratio' in results
        assert 'total_return' in results
        assert 'equity_curve' in results
        assert 'max_drawdown' in results
        assert 'win_rate' in results


class TestStrategies:
    def test_sma_crossover(self, sample_price_series):
        signals = TradingStrategies.sma_crossover(sample_price_series)
        assert len(signals) == len(sample_price_series)
        assert all(s in [0, 1] for s in signals.dropna())
    
    def test_ema_crossover(self, sample_price_series):
        signals = TradingStrategies.ema_crossover(sample_price_series)
        assert len(signals) == len(sample_price_series)
    
    def test_rsi_strategy(self, sample_price_series):
        signals = TradingStrategies.rsi_strategy(sample_price_series)
        assert len(signals) == len(sample_price_series)
    
    def test_macd_strategy(self, sample_price_series):
        signals = TradingStrategies.macd_strategy(sample_price_series)
        assert len(signals) == len(sample_price_series)
    
    def test_bollinger_bands(self, sample_price_series):
        signals = TradingStrategies.bollinger_bands(sample_price_series)
        assert len(signals) == len(sample_price_series)
    
    def test_momentum(self, sample_price_series):
        signals = TradingStrategies.momentum(sample_price_series)
        assert len(signals) == len(sample_price_series)


class TestRiskMetrics:
    def test_sharpe_ratio(self, sample_price_series):
        returns = sample_price_series.pct_change()
        sharpe = RiskMetrics.calculate_sharpe_ratio(returns)
        assert isinstance(sharpe, float)
    
    def test_sortino_ratio(self, sample_price_series):
        returns = sample_price_series.pct_change()
        sortino = RiskMetrics.calculate_sortino_ratio(returns)
        assert isinstance(sortino, float)
    
    def test_calmar_ratio(self, sample_price_series):
        returns = sample_price_series.pct_change()
        calmar = RiskMetrics.calculate_calmar_ratio(returns, sample_price_series)
        assert isinstance(calmar, float)
    
    def test_var(self, sample_price_series):
        returns = sample_price_series.pct_change()
        var = RiskMetrics.calculate_var(returns)
        assert var < 0
    
    def test_cvar(self, sample_price_series):
        returns = sample_price_series.pct_change()
        cvar = RiskMetrics.calculate_cvar(returns)
        assert isinstance(cvar, (int, float))
    
    def test_win_rate(self, sample_price_series):
        returns = sample_price_series.pct_change()
        win_rate = RiskMetrics.calculate_win_rate(returns)
        assert 0 <= win_rate <= 1
    
    def test_profit_factor(self, sample_price_series):
        returns = sample_price_series.pct_change()
        pf = RiskMetrics.calculate_profit_factor(returns)
        assert isinstance(pf, (int, float))


class TestFormatter:
    def test_format_currency(self):
        from utils import Formatter
        result = Formatter.format_currency(1000.5)
        assert "₹" in result
        assert "1,000.50" in result
    
    def test_format_percentage(self):
        from utils import Formatter
        result = Formatter.format_percentage(0.05)
        assert "%" in result
        assert "5.00" in result
    
    def test_format_ratio(self):
        from utils import Formatter
        result = Formatter.format_ratio(1.5)
        assert "1.50" in result


class TestIntegration:
    def test_full_backtest_pipeline(self, sample_price_series):
        signals = TradingStrategies.sma_crossover(sample_price_series)
        backtester = QuantBacktester()
        results = backtester.backtest_strategy(sample_price_series, signals, "SMA Test")
        
        assert results['strategy_name'] == "SMA Test"
        assert len(results['equity_curve']) > 0
        assert 'sharpe_ratio' in results
        assert 'sortino_ratio' in results
        assert 'calmar_ratio' in results


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=."])
