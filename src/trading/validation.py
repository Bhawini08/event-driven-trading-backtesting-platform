from __future__ import annotations
import pandas as pd
from .engine import BacktestEngine
from .execution import ExecutionModel
from .metrics import performance_metrics

def walk_forward(prices: pd.DataFrame, strategy_factory, train=252, test=126, step=126, costs=None):
    """Chronological OOS validation.

    The training slice is used only as signal-history warmup. Portfolio cash and positions
    remain untouched until the first test date, so OOS performance and trade diagnostics
    contain no in-sample trading activity.
    """
    rows=[]; costs=costs or ExecutionModel()
    for start in range(0,len(prices)-train-test+1,step):
        warmup=prices.iloc[start:start+train].copy()
        test_px=prices.iloc[start+train:start+train+test].copy()
        combined=pd.concat([warmup,test_px])
        strat=strategy_factory()
        engine=BacktestEngine(
            combined,
            strat,
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

def cost_sensitivity(prices, strategy_factory, grid=(0.5,1,2,5)):
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
