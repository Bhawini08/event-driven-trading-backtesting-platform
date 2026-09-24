from __future__ import annotations
import pandas as pd
from .engine import BacktestEngine
from .execution import ExecutionModel
from .metrics import performance_metrics

def walk_forward(prices: pd.DataFrame, strategy_factory, train=252, test=126, step=126, costs=None):
    rows=[]; costs=costs or ExecutionModel()
    for start in range(0,len(prices)-train-test+1,step):
        warmup=prices.iloc[start:start+train].copy()
        test_px=prices.iloc[start+train:start+train+test].copy()
        combined=pd.concat([warmup,test_px])
        engine=BacktestEngine(
            combined,
            strategy_factory(),
            execution=costs,
            trading_start=test_px.index[0],
        )
        curve,trades=engine.run()
        oos_curve=curve.loc[test_px.index].copy()
        oos_trades=trades.copy()
        if not oos_trades.empty:
            oos_trades["timestamp"]=pd.to_datetime(oos_trades["timestamp"])
            oos_trades=oos_trades[oos_trades["timestamp"]>=pd.Timestamp(test_px.index[0])]
        m=performance_metrics(oos_curve.equity,oos_trades)
        rows.append({
            "train_start":warmup.index[0],
            "train_end":warmup.index[-1],
            "test_start":test_px.index[0],
            "test_end":test_px.index[-1],
            **m
        })
    return pd.DataFrame(rows)

def cost_sensitivity(prices, strategy_factory, grid=(0.0,0.5,1,2,5)):
    rows=[]
    for bps in grid:
        ex=ExecutionModel(
            commission_bps=bps/4,
            slippage_bps=bps/4,
            half_spread_bps=bps/2
        )
        curve,trades=BacktestEngine(prices,strategy_factory(),execution=ex).run()
        m=performance_metrics(curve.equity,trades)
        rows.append({"total_cost_bps":bps,**m})
    return pd.DataFrame(rows)

def parameter_robustness(prices, strategy_builders: dict[str, callable]):
    rows=[]
    for label,builder in strategy_builders.items():
        curve,trades=BacktestEngine(prices,builder()).run()
        rows.append({"specification":label,**performance_metrics(curve.equity,trades)})
    return pd.DataFrame(rows)

def benchmark_metrics(prices: pd.DataFrame, symbol="SPY"):
    px=prices[symbol].dropna()
    equity=1_000_000*(px/px.iloc[0])
    return performance_metrics(equity)
