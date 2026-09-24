import numpy as np
from trading.data import synthetic_prices
from trading.engine import BacktestEngine
from trading.strategies import MomentumStrategy, MeanReversionStrategy, PairsStrategy
from trading.execution import ExecutionModel
from trading.metrics import performance_metrics
from trading.validation import walk_forward

def test_engine_accounting_and_costs():
    px=synthetic_prices(350)
    curve,trades=BacktestEngine(px,MomentumStrategy(30),execution=ExecutionModel(1,2,3)).run()
    assert len(curve)==len(px)
    assert curve.equity.notna().all()
    assert "pnl" in curve.columns and "period_pnl" in curve.columns
    assert np.allclose(curve["pnl"],curve["equity"]-1_000_000)
    assert (trades.commission>=0).all() and (trades.slippage_cost>=0).all()

def test_three_strategies_run():
    px=synthetic_prices(300)
    for s in [MomentumStrategy(30),MeanReversionStrategy(10),PairsStrategy("SPY","QQQ",30)]:
        curve,_=BacktestEngine(px,s).run(); m=performance_metrics(curve.equity)
        assert np.isfinite(m["annualized_volatility"])

def test_walk_forward_is_chronological():
    px=synthetic_prices(700)
    wf=walk_forward(px,lambda:MomentumStrategy(30),train=252,test=63,step=63)
    assert len(wf)>0
    assert (wf.train_end < wf.test_start).all()
    assert wf["annualized_return"].notna().all()
