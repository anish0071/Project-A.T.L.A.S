from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

from backtest import QuantBacktester, BacktestConfig
from strategies import get_strategy, STRATEGY_CONFIGS
from data import DataFetcher

app = FastAPI(title="Quant Backtester API", version="1.0.0")


class BacktestRequest(BaseModel):
    ticker: str
    period: str = "5y"
    strategy_name: str
    parameters: Dict = {}
    initial_cash: float = 100000


class BacktestResponse(BaseModel):
    request_id: str
    strategy_name: str
    ticker: str
    total_return: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    annual_return: float
    annual_volatility: float
    win_rate: float
    total_trades: int
    status: str = "completed"


@app.get("/")
async def root():
    return {"message": "Quant Backtester API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/strategies")
async def list_strategies():
    return {"total": len(STRATEGY_CONFIGS), "strategies": list(STRATEGY_CONFIGS.keys())}


@app.get("/tickers")
async def list_tickers():
    tickers = DataFetcher.get_available_tickers()
    return {"total": len(tickers), "tickers": tickers}


@app.post("/backtest")
async def run_backtest(request: BacktestRequest):
    try:
        data = DataFetcher.fetch_historical_data(request.ticker, period=request.period)
        if data.empty:
            raise HTTPException(status_code=400, detail=f"No data for {request.ticker}")
        
        prices = data['close']
        strategy_func = get_strategy(request.strategy_name)
        signals = strategy_func(prices, **request.parameters)
        
        backtester = QuantBacktester(BacktestConfig(initial_cash=request.initial_cash))
        results = backtester.backtest_strategy(prices, signals, request.strategy_name)
        
        return BacktestResponse(
            request_id=f"REQ_{datetime.now().timestamp()}",
            strategy_name=request.strategy_name,
            ticker=request.ticker,
            total_return=results['total_return'],
            sharpe_ratio=results['sharpe_ratio'],
            sortino_ratio=results['sortino_ratio'],
            calmar_ratio=results['calmar_ratio'],
            max_drawdown=results['max_drawdown'],
            annual_return=results['annual_return'],
            annual_volatility=results['annual_volatility'],
            win_rate=results['win_rate'],
            total_trades=int(results['total_trades']),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/definition")
async def metrics_definition():
    return {
        "sharpe_ratio": "Risk-adjusted return metric",
        "sortino_ratio": "Similar to Sharpe but only penalizes downside",
        "calmar_ratio": "Annual return / Max drawdown",
        "max_drawdown": "Largest peak-to-trough decline",
        "win_rate": "% of profitable trades",
    }


@app.post("/backtest/batch")
async def batch_backtest(requests: List[BacktestRequest]):
    results = []
    for req in requests:
        try:
            data = DataFetcher.fetch_historical_data(req.ticker, period=req.period)
            if not data.empty:
                prices = data['close']
                strategy_func = get_strategy(req.strategy_name)
                signals = strategy_func(prices, **req.parameters)
                backtester = QuantBacktester(BacktestConfig(initial_cash=req.initial_cash))
                result = backtester.backtest_strategy(prices, signals, req.strategy_name)
                
                results.append(BacktestResponse(
                    request_id=f"REQ_{datetime.now().timestamp()}",
                    strategy_name=req.strategy_name,
                    ticker=req.ticker,
                    total_return=result['total_return'],
                    sharpe_ratio=result['sharpe_ratio'],
                    sortino_ratio=result['sortino_ratio'],
                    calmar_ratio=result['calmar_ratio'],
                    max_drawdown=result['max_drawdown'],
                    annual_return=result['annual_return'],
                    annual_volatility=result['annual_volatility'],
                    win_rate=result['win_rate'],
                    total_trades=int(result['total_trades']),
                ))
        except:
            pass
    
    return {"total": len(requests), "successful": len(results), "results": results}
