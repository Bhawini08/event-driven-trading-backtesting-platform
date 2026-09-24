import numpy as np
from trading.data import synthetic_prices
from trading.engine import BacktestEngine
from trading.strategies import MomentumStrategy, MeanReversionStrategy, PairsStrategy
from trading.execution import ExecutionModel
from trading.metrics import performance_metrics
from trading.validation import walk_forward, cost_sensitivity, parameter_robustness

def test_engine_accounting_and_costs():
    px=synthetic_prices(350)
    curve,trades=BacktestEngine(px,MomentumStrategy(30),execution=ExecutionModel(1,2,3)).run()
    assert len(curve)==len(px)
    assert curve.equity.notna().all()
    assert "pnl" in curve.columns and "period_pnl" in curve.columns
    assert np.allclose(curve["pnl"],curve["equity"]-1_000_000)
    assert (trades.commission>=0).all() and (trades.slippage_cost>=0).all()
    assert curve.gross_exposure.max() <= 1.02

def test_three_strategies_run():
    px=synthetic_prices(350)
    for s in [MomentumStrategy(30),MeanReversionStrategy(10),PairsStrategy("SPY","QQQ",60)]:
        curve,_=BacktestEngine(px,s).run()
        m=performance_metrics(curve.equity)
        assert np.isfinite(m["annualized_volatility"])
        assert curve.gross_exposure.max() <= 1.02

def test_walk_forward_is_chronological():
    px=synthetic_prices(700)
    wf=walk_forward(px,lambda:MomentumStrategy(30),train=252,test=63,step=63)
    assert len(wf)>0
    assert (wf.train_end < wf.test_start).all()
    assert wf["annualized_return"].notna().all()

def test_cost_and_parameter_diagnostics():
    px=synthetic_prices(400)
    c=cost_sensitivity(px,lambda:MomentumStrategy(30),grid=(0,1,5))
    assert list(c.total_cost_bps)==[0,1,5]
    p=parameter_robustness(px,{"m20":lambda:MomentumStrategy(20),"m60":lambda:MomentumStrategy(60)})
    assert set(p.specification)=={"m20","m60"}

def test_pairs_diagnostics_and_exact_target_gross():
    px=synthetic_prices(350)
    s=PairsStrategy("SPY","QQQ",lookback=60,entry_z=0.5,cointegration_p=1.0,adf_p=1.0)
    d=s.diagnostics(px.iloc[:200])
    assert {"beta","zscore","cointegration_p","spread_adf_p"}.issubset(d)
    t=s.targets(px.iloc[:200])
    assert sum(abs(x) for x in t.values()) <= 1.000001
