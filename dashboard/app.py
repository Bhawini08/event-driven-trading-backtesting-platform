import streamlit as st
import pandas as pd
from pathlib import Path
st.set_page_config(page_title="Trading Backtest Platform",layout="wide")
st.title("Event-Driven Multi-Strategy Trading & Backtesting Platform")
p=Path("results/strategy_summary.csv")
if not p.exists():
    st.info("Run scripts/run_backtest.py --mode synthetic or the later live-data pass first.")
else:
    s=pd.read_csv(p); st.dataframe(s,use_container_width=True)
    c=Path("results/strategy_correlation.csv")
    if c.exists(): st.subheader("Strategy correlation"); st.dataframe(pd.read_csv(c,index_col=0),use_container_width=True)
    wf=Path("results/walk_forward.csv")
    if wf.exists(): st.subheader("Walk-forward validation"); st.dataframe(pd.read_csv(wf),use_container_width=True)
