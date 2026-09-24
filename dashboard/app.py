import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Trading Backtest Platform",layout="wide")
st.title("Event-Driven Multi-Strategy Trading & Backtesting Platform")

results=Path("results")
summary_path=results/"strategy_summary.csv"

if not summary_path.exists():
    st.info("Run scripts/run_backtest.py --mode synthetic or --mode live first.")
    st.stop()

summary=pd.read_csv(summary_path)
benchmark_path=results/"benchmark_summary.csv"

st.subheader("Strategy summary")
st.dataframe(summary,use_container_width=True)

if benchmark_path.exists():
    benchmark=pd.read_csv(benchmark_path)
    st.subheader("Benchmark")
    st.dataframe(benchmark,use_container_width=True)

tabs=st.tabs(["Equity Curves","Walk-Forward","Cost Sensitivity","Parameter Robustness","Correlation"])

with tabs[0]:
    curves={}
    for name in ["momentum","mean_reversion","pairs"]:
        p=results/(name+"_equity.csv")
        if p.exists():
            x=pd.read_csv(p,index_col=0,parse_dates=True)
            curves[name]=x["equity"]/x["equity"].iloc[0]
    if curves:
        st.line_chart(pd.DataFrame(curves))

with tabs[1]:
    p=results/"walk_forward.csv"
    if p.exists():
        wf=pd.read_csv(p)
        st.dataframe(wf,use_container_width=True)
        if {"strategy","annualized_return"}.issubset(wf.columns):
            agg=wf.groupby("strategy").agg(
                mean_annualized_return=("annualized_return","mean"),
                median_annualized_return=("annualized_return","median"),
                positive_windows=("annualized_return",lambda x:(x>0).sum()),
                windows=("annualized_return","size")
            )
            st.subheader("OOS summary")
            st.dataframe(agg,use_container_width=True)

with tabs[2]:
    p=results/"cost_sensitivity.csv"
    if p.exists():
        x=pd.read_csv(p)
        st.dataframe(x,use_container_width=True)
        pivot=x.pivot(index="total_cost_bps",columns="strategy",values="annualized_return")
        st.line_chart(pivot)

with tabs[3]:
    p=results/"parameter_robustness.csv"
    if p.exists():
        x=pd.read_csv(p)
        st.dataframe(x,use_container_width=True)
        st.bar_chart(x.set_index("specification")[["annualized_return"]])

with tabs[4]:
    p=results/"strategy_correlation.csv"
    if p.exists():
        st.dataframe(pd.read_csv(p,index_col=0),use_container_width=True)

st.caption("Live validation is intentionally retained even when strategies underperform. The platform is designed for signal rejection as well as signal discovery.")
