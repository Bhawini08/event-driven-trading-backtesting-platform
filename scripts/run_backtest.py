import argparse, json
from pathlib import Path
import pandas as pd
from trading.data import synthetic_prices, live_prices
from trading.strategies import MomentumStrategy, MeanReversionStrategy, PairsStrategy
from trading.engine import BacktestEngine
from trading.metrics import performance_metrics
from trading.validation import cost_sensitivity, walk_forward, parameter_robustness, benchmark_metrics

p=argparse.ArgumentParser()
p.add_argument("--mode",default="synthetic",choices=["synthetic","live"])
p.add_argument("--outdir",default="results")
a=p.parse_args()
out=Path(a.outdir); out.mkdir(exist_ok=True)

prices=synthetic_prices() if a.mode=="synthetic" else live_prices()
strategies=[
    MomentumStrategy(),
    MeanReversionStrategy(),
    PairsStrategy("SPY","QQQ")
]

summary=[]; returns={}
for s in strategies:
    curve,trades=BacktestEngine(prices,s).run()
    curve.to_csv(out/f"{s.name}_equity.csv")
    trades.to_csv(out/f"{s.name}_trades.csv",index=False)
    m=performance_metrics(curve.equity,trades)
    summary.append({"strategy":s.name,**m})
    returns[s.name]=curve.equity.pct_change()

summary_df=pd.DataFrame(summary)
summary_df.to_csv(out/"strategy_summary.csv",index=False)
pd.DataFrame(returns).corr().to_csv(out/"strategy_correlation.csv")

# Walk-forward each strategy with the same chronological protocol.
wf_frames=[]
factories={
    "momentum":lambda:MomentumStrategy(),
    "mean_reversion":lambda:MeanReversionStrategy(),
    "pairs":lambda:PairsStrategy("SPY","QQQ"),
}
for name,factory in factories.items():
    wf=walk_forward(prices,factory)
    wf.insert(0,"strategy",name)
    wf_frames.append(wf)
pd.concat(wf_frames,ignore_index=True).to_csv(out/"walk_forward.csv",index=False)

# Strategy-specific implementation-cost sensitivity.
cost_frames=[]
for name,factory in factories.items():
    c=cost_sensitivity(prices,factory)
    c.insert(0,"strategy",name)
    cost_frames.append(c)
pd.concat(cost_frames,ignore_index=True).to_csv(out/"cost_sensitivity.csv",index=False)

# Reasonable parameter neighborhoods, reported rather than optimized.
robustness={
    "mom_20":lambda:MomentumStrategy(20),
    "mom_60":lambda:MomentumStrategy(60),
    "mom_120":lambda:MomentumStrategy(120),
    "mr_5":lambda:MeanReversionStrategy(5),
    "mr_20":lambda:MeanReversionStrategy(20),
    "mr_60":lambda:MeanReversionStrategy(60),
    "pairs_60":lambda:PairsStrategy("SPY","QQQ",lookback=60),
    "pairs_120":lambda:PairsStrategy("SPY","QQQ",lookback=120),
    "pairs_252":lambda:PairsStrategy("SPY","QQQ",lookback=252),
}
parameter_robustness(prices,robustness).to_csv(out/"parameter_robustness.csv",index=False)

bench=benchmark_metrics(prices,"SPY")
pd.DataFrame([{"benchmark":"SPY_buy_and_hold",**bench}]).to_csv(out/"benchmark_summary.csv",index=False)

print(json.dumps({
    "mode":a.mode,
    "strategies":summary,
    "benchmark":bench,
},indent=2,default=float))
