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
