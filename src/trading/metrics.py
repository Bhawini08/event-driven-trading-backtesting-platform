import numpy as np
import pandas as pd

def max_drawdown(r):
    wealth=(1+r.fillna(0)).cumprod(); dd=wealth/wealth.cummax()-1
    return float(dd.min())

def performance_metrics(equity: pd.Series, trades: pd.DataFrame|None=None, periods=252):
    r=equity.pct_change().dropna()
    ann=(equity.iloc[-1]/equity.iloc[0])**(periods/max(len(r),1))-1 if len(equity)>1 else 0.0
    vol=r.std(ddof=1)*np.sqrt(periods) if len(r)>1 else 0.0
    sharpe=(r.mean()/r.std(ddof=1)*np.sqrt(periods)) if r.std(ddof=1)>0 else np.nan
    downside=np.sqrt(np.mean(np.minimum(r,0)**2))*np.sqrt(periods) if len(r) else 0.0
    sortino=(r.mean()*periods/downside) if downside>0 else np.nan
    mdd=max_drawdown(r); calmar=ann/abs(mdd) if mdd<0 else np.nan
    out={"annualized_return":float(ann),"annualized_volatility":float(vol),"sharpe":float(sharpe),
         "sortino":float(sortino),"max_drawdown":mdd,"calmar":float(calmar)}
    if trades is not None and not trades.empty:
        notionals=(trades.quantity.abs()*trades.price).astype(float)
        out["turnover_notional"]=float(notionals.sum())
        out["transaction_costs"]=float((trades.commission+trades.slippage_cost+trades.spread_cost).sum())
    return out

def trade_statistics(trade_pnl: pd.Series):
    if len(trade_pnl)==0: return {"hit_rate":np.nan,"profit_factor":np.nan}
    wins=trade_pnl[trade_pnl>0].sum(); losses=-trade_pnl[trade_pnl<0].sum()
    return {"hit_rate":float((trade_pnl>0).mean()),"profit_factor":float(wins/losses) if losses>0 else np.inf}
