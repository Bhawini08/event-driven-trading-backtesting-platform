import argparse, json
from pathlib import Path
import pandas as pd
from trading.data import synthetic_prices
from trading.strategies import MomentumStrategy, MeanReversionStrategy, PairsStrategy
from trading.engine import BacktestEngine
from trading.metrics import performance_metrics
from trading.validation import cost_sensitivity, walk_forward

p=argparse.ArgumentParser(); p.add_argument("--mode",default="synthetic"); p.add_argument("--outdir",default="results")
a=p.parse_args(); out=Path(a.outdir); out.mkdir(exist_ok=True)
if a.mode!="synthetic": raise SystemExit("Live mode will be validated in the final market-data pass.")
prices=synthetic_prices(); strategies=[MomentumStrategy(),MeanReversionStrategy(),PairsStrategy("SPY","QQQ")]
summary=[]; returns={}
for s in strategies:
    curve,trades=BacktestEngine(prices,s).run(); curve.to_csv(out/f"{s.name}_equity.csv"); trades.to_csv(out/f"{s.name}_trades.csv",index=False)
    m=performance_metrics(curve.equity,trades); summary.append({"strategy":s.name,**m}); returns[s.name]=curve.equity.pct_change()
pd.DataFrame(summary).to_csv(out/"strategy_summary.csv",index=False)
pd.DataFrame(returns).corr().to_csv(out/"strategy_correlation.csv")
cost_sensitivity(prices,lambda:MomentumStrategy()).to_csv(out/"cost_sensitivity.csv",index=False)
walk_forward(prices,lambda:MomentumStrategy()).to_csv(out/"walk_forward.csv",index=False)
print(json.dumps(summary,indent=2,default=float))
