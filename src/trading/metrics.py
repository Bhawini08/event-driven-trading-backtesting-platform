import numpy as np
import pandas as pd

def max_drawdown(r):
    wealth=(1+r.fillna(0)).cumprod(); dd=wealth/wealth.cummax()-1
    return float(dd.min())

def round_trip_statistics(trades: pd.DataFrame):
    """Approximate realized trade episodes from the fill ledger using average-cost accounting."""
    if trades is None or trades.empty:
        return {"hit_rate":np.nan,"profit_factor":np.nan,"average_holding_period_days":np.nan,"round_trips":0}
    x=trades.copy()
    x["timestamp"]=pd.to_datetime(x["timestamp"])
    x=x.sort_values("timestamp")
    states={}
    realized=[]
    for row in x.itertuples():
        s=row.symbol; q=float(row.quantity); px=float(row.price)
        cost=float(row.commission)+float(row.slippage_cost)+float(row.spread_cost)
        st=states.setdefault(s,{"pos":0.0,"avg":0.0,"entry":None})
        pos=st["pos"]
        if abs(pos)<1e-12:
            st.update(pos=q,avg=px,entry=row.timestamp)
            continue
        if np.sign(pos)==np.sign(q):
            new=pos+q
            st["avg"]=(abs(pos)*st["avg"]+abs(q)*px)/abs(new)
            st["pos"]=new
            continue
        closed=min(abs(pos),abs(q))
        pnl=closed*(px-st["avg"])*np.sign(pos)-cost
        holding=(row.timestamp-st["entry"]).days if st["entry"] is not None else np.nan
        realized.append({"symbol":s,"pnl":pnl,"holding_days":holding})
        new=pos+q
        if abs(new)<1e-12:
            st.update(pos=0.0,avg=0.0,entry=None)
        elif np.sign(new)!=np.sign(pos):
            st.update(pos=new,avg=px,entry=row.timestamp)
        else:
            st["pos"]=new
    if not realized:
        return {"hit_rate":np.nan,"profit_factor":np.nan,"average_holding_period_days":np.nan,"round_trips":0}
    r=pd.DataFrame(realized)
    wins=r.loc[r.pnl>0,"pnl"].sum(); losses=-r.loc[r.pnl<0,"pnl"].sum()
    return {"hit_rate":float((r.pnl>0).mean()),
            "profit_factor":float(wins/losses) if losses>0 else np.inf,
            "average_holding_period_days":float(r.holding_days.mean()),
            "round_trips":int(len(r))}

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
        years=max(len(r)/periods,1/periods)
        out["turnover"]=float(notionals.sum()/(2*equity.mean())/years)
        out["transaction_costs"]=float((trades.commission+trades.slippage_cost+trades.spread_cost).sum())
        out.update(round_trip_statistics(trades))
    return out
