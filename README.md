# Event-Driven Multi-Strategy Trading & Backtesting Platform

A production-style research engine for testing systematic strategies under realistic portfolio, execution, and transaction-cost assumptions.

The platform separates **market events, strategy signals, orders, fills, positions, cash, P&L, exposures, and diagnostics** rather than treating a backtest as a single vectorized return calculation.

## Strategies

- Cross-sectional/time-series momentum
- Mean reversion
- Pairs / statistical arbitrage

## Engine features

- Event-driven processing
- Orders and fills
- Position sizing
- Cash and mark-to-market accounting
- Gross/net exposure
- Commissions, slippage, and variable bid-ask spread assumptions
- Trade ledger and portfolio equity curve
- Cost sensitivity
- Strategy correlation
- Walk-forward / out-of-sample validation

## Diagnostics

Annualized return, volatility, Sharpe, Sortino, maximum drawdown, Calmar, hit rate, profit factor, turnover, average holding period, exposure, and transaction-cost sensitivity.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
pytest -q
python scripts/run_backtest.py --mode synthetic
```

Live market-data validation can be added after the deterministic research fixture passes.

## Research discipline

The synthetic dataset is an engineering fixture, not evidence of trading alpha. Strategy conclusions should be based on live or independently sourced market data, chronological splits, and cost-aware out-of-sample validation.
