import numpy as np
import pandas as pd

def synthetic_prices(n=1000, seed=7):
    rng=np.random.default_rng(seed); idx=pd.bdate_range("2018-01-01",periods=n)
    market=rng.normal(0.00025,0.01,n)
    data={}
    for i,s in enumerate(["SPY","QQQ","IWM","XLF","XLK","XLE"]):
        noise=rng.normal(0,0.006+0.001*i,n)
        ret=0.8*market+noise+0.00005*np.sin(np.arange(n)/20+i)
        data[s]=100*np.exp(np.cumsum(ret))
    # force one stable pair component
    data["QQQ"]=np.array(data["SPY"])*1.2*np.exp(rng.normal(0,0.03,n))
    return pd.DataFrame(data,index=idx)


def live_prices(tickers=None,start="2015-01-01",end=None):
    """Download adjusted daily closes for the live validation pass."""
    import yfinance as yf
    tickers=tickers or ["SPY","QQQ","IWM","XLF","XLK","XLE"]
    raw=yf.download(tickers,start=start,end=end,auto_adjust=True,progress=False,threads=False)
    if raw.empty: raise RuntimeError("Yahoo Finance returned no data")
    if isinstance(raw.columns,pd.MultiIndex):
        px=raw["Close"] if "Close" in raw.columns.get_level_values(0) else raw.xs("Close",axis=1,level=1)
    else:
        px=raw[["Close"]].copy(); px.columns=[tickers[0]]
    px.columns=[str(x).upper() for x in px.columns]
    return px.dropna(how="any")
