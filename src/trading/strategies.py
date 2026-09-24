from __future__ import annotations
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint, adfuller

class MomentumStrategy:
    name="momentum"
    def __init__(self, lookback=60, gross=1.0):
        self.lookback,self.gross=lookback,gross
    def targets(self, history: pd.DataFrame) -> dict[str,float]:
        if len(history)<self.lookback+1:
            return {c:0.0 for c in history.columns}
        score=history.iloc[-1]/history.iloc[-self.lookback]-1
        z=(score-score.mean())/(score.std(ddof=0)+1e-12)
        raw=z.clip(-2,2)
        denom=raw.abs().sum()
        return (self.gross*raw/denom if denom else raw*0).to_dict()

class MeanReversionStrategy:
    name="mean_reversion"
    def __init__(self, lookback=20, gross=1.0):
        self.lookback,self.gross=lookback,gross
    def targets(self, history: pd.DataFrame) -> dict[str,float]:
        if len(history)<self.lookback+1:
            return {c:0.0 for c in history.columns}
        rets=history.pct_change(fill_method=None).dropna().tail(self.lookback)
        if len(rets)<self.lookback:
            return {c:0.0 for c in history.columns}
        # Cross-sectional reversal uses the most recent completed return,
        # standardized against each asset's own recent return distribution.
        last=rets.iloc[-1]
        mu=rets.mean()
        sd=rets.std(ddof=0).replace(0,np.nan)
        z=((last-mu)/sd).replace([np.inf,-np.inf],np.nan).fillna(0.0)
        raw=(-z).clip(-2,2)
        denom=raw.abs().sum()
        return (self.gross*raw/denom if denom else raw*0).to_dict()

class PairsStrategy:
    name="pairs"
    def __init__(
        self,a,b,lookback=120,gross=1.0,entry_z=1.5,exit_z=0.35,
        cointegration_p=0.10,adf_p=0.10,max_holding_rebalances=20
    ):
        self.a,self.b,self.lookback,self.gross=a,b,lookback,gross
        self.entry_z,self.exit_z=entry_z,exit_z
        self.cointegration_p,self.adf_p=cointegration_p,adf_p
        self.max_holding_rebalances=max_holding_rebalances
        self.side=0.0
        self.hold_count=0

    def diagnostics(self, history: pd.DataFrame) -> dict[str,float]:
        if len(history)<self.lookback:
            return {"beta":np.nan,"zscore":np.nan,"cointegration_p":np.nan,"spread_adf_p":np.nan}
        x=np.log(history[self.a].tail(self.lookback).astype(float))
        y=np.log(history[self.b].tail(self.lookback).astype(float))
        beta=np.polyfit(x,y,1)[0]
        spread=y-beta*x
        z=float((spread.iloc[-1]-spread.mean())/(spread.std(ddof=0)+1e-12))
        try:
            coint_p=float(coint(y,x)[1])
        except Exception:
            coint_p=np.nan
        try:
            adf_p=float(adfuller(spread,autolag="AIC",result_object=False)[1])
        except Exception:
            adf_p=np.nan
        return {"beta":float(beta),"zscore":z,"cointegration_p":coint_p,"spread_adf_p":adf_p}

    def targets(self, history: pd.DataFrame) -> dict[str,float]:
        out={c:0.0 for c in history.columns}
        if len(history)<self.lookback:
            return out
        d=self.diagnostics(history)
        beta,z,coint_p,adf_p=d["beta"],d["zscore"],d["cointegration_p"],d["spread_adf_p"]
        stable=np.isfinite(coint_p) and np.isfinite(adf_p) and coint_p<=self.cointegration_p and adf_p<=self.adf_p
        if not stable:
            self.side=0.0; self.hold_count=0
            return out

        if self.side==0:
            if abs(z)<self.entry_z:
                return out
            self.side=-float(np.sign(z))
            self.hold_count=0
        else:
            self.hold_count+=1
            if abs(z)<=self.exit_z or self.hold_count>=self.max_holding_rebalances or np.sign(z)==self.side:
                self.side=0.0; self.hold_count=0
                return out

        # Dollar gross is exactly self.gross while preserving the hedge ratio.
        denom=1.0+abs(beta)
        out[self.a]=-self.side*self.gross*abs(beta)/denom
        out[self.b]=self.side*self.gross/denom
        return out
