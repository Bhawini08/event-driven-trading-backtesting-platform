from __future__ import annotations
import numpy as np
import pandas as pd

class MomentumStrategy:
    name="momentum"
    def __init__(self, lookback=60, gross=1.0): self.lookback,self.gross=lookback,gross
    def targets(self, history: pd.DataFrame) -> dict[str,float]:
        if len(history)<self.lookback+1: return {c:0.0 for c in history.columns}
        score=history.iloc[-1]/history.iloc[-self.lookback]-1
        z=(score-score.mean())/(score.std(ddof=0)+1e-12)
        raw=z.clip(-2,2)
        denom=raw.abs().sum()
        return (self.gross*raw/denom if denom else raw*0).to_dict()

class MeanReversionStrategy:
    name="mean_reversion"
    def __init__(self, lookback=20, gross=1.0): self.lookback,self.gross=lookback,gross
    def targets(self, history: pd.DataFrame) -> dict[str,float]:
        if len(history)<self.lookback: return {c:0.0 for c in history.columns}
        rets=history.pct_change().tail(self.lookback)
        z=(rets.iloc[-1]-rets.mean())/(rets.std(ddof=0)+1e-12)
        raw=(-z).clip(-2,2); denom=raw.abs().sum()
        return (self.gross*raw/denom if denom else raw*0).to_dict()

class PairsStrategy:
    name="pairs"
    def __init__(self, a, b, lookback=60, gross=1.0): self.a,self.b,self.lookback,self.gross=a,b,lookback,gross
    def targets(self, history: pd.DataFrame) -> dict[str,float]:
        out={c:0.0 for c in history.columns}
        if len(history)<self.lookback: return out
        x=np.log(history[self.a].tail(self.lookback)); y=np.log(history[self.b].tail(self.lookback))
        beta=np.polyfit(x,y,1)[0]; spread=y-beta*x
        z=(spread.iloc[-1]-spread.mean())/(spread.std(ddof=0)+1e-12)
        if abs(z)<0.75: return out
        side=-np.sign(z)
        out[self.a]=-side*self.gross/(1+abs(beta)); out[self.b]=side*self.gross/(1+abs(beta))
        return out
