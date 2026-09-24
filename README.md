# Event-Driven Multi-Strategy Trading & Backtesting Platform

A production-style research engine for testing systematic strategies under realistic portfolio, execution, and transaction-cost assumptions.

The platform separates **strategy signals, orders, fills, positions, cash, P&L, exposures, transaction costs, and out-of-sample validation** rather than treating a backtest as a single vectorized return calculation.

## Strategies

- Cross-sectional momentum
- Short-horizon mean reversion
- Pairs / statistical arbitrage with cointegration and spread-stationarity filters

## Engine features

- Event-driven portfolio accounting
- Orders and fills
- Position sizing
- Cash and mark-to-market P&L
- Gross/net exposure
- Hard gross-exposure cap with mark-to-market deleveraging
- Commissions, slippage, and variable spread assumptions
- Trade ledger and equity curve
- Same-close look-ahead protection: signals are formed from information through the prior bar and executed on the next bar
- Walk-forward / out-of-sample validation
- Parameter robustness
- Cost sensitivity
- SPY buy-and-hold benchmark

## Live research snapshot

The final live validation uses adjusted daily market data across:

`SPY, QQQ, IWM, XLF, XLK, XLE`

Full-sample results:

| Strategy | Ann. return | Sharpe | Max drawdown | Turnover | Profit factor |
| --- | ---: | ---: | ---: | ---: | ---: |
| Momentum | -2.54% | -0.20 | -33.5% | 10.5x | 0.88 |
| Mean reversion | -4.01% | -0.14 | -52.0% | 33.2x | 0.86 |
| Pairs | +0.07% | 0.14 | -1.30% | 0.52x | 1.14 |
| SPY buy-and-hold | +13.79% | 0.82 | -33.7% | n/a | n/a |

The project deliberately keeps these weak results. The research conclusion is that the tested momentum and mean-reversion specifications do **not** demonstrate robust alpha in this universe, while the filtered pairs model trades infrequently and exhibits low drawdown but negligible economic return.

## Walk-forward findings

Each strategy is evaluated over 21 chronological OOS windows.

- Momentum: mean OOS annualized return **-0.31%**, median **-2.29%**, 9/21 positive windows.
- Mean reversion: mean OOS annualized return **-1.49%**, median **-7.92%**, 8/21 positive windows.
- Pairs: mean OOS annualized return **+0.22%**, median **0.00%**, 5/21 positive windows.

These results reinforce the distinction between a working backtesting platform and a profitable strategy.

## Parameter robustness

Reasonable parameter neighborhoods are reported instead of tuned away:

- Momentum 20/60/120-day lookbacks produce mixed outcomes.
- Mean-reversion 5/20/60-day lookbacks remain weak.
- Pairs 60/120/252-day lookbacks remain economically small.

This avoids presenting a single hand-picked parameter choice as evidence of persistent alpha.

## Diagnostics

Annualized return, volatility, Sharpe, Sortino, maximum drawdown, Calmar, hit rate, profit factor, turnover, average holding period, strategy correlation, transaction costs, cost sensitivity, and OOS stability.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
pytest -q
python scripts/run_backtest.py --mode synthetic
```

For live validation:

```bash
python scripts/run_backtest.py --mode live
```

Then:

```bash
streamlit run dashboard/app.py
```

## Research discipline

The synthetic dataset is an engineering fixture, not evidence of trading alpha. Live results are reported with benchmark comparison, realistic implementation costs, parameter sensitivity, exposure controls, and chronological OOS evaluation.

A high-quality research platform should be capable of rejecting weak strategies rather than optimizing until every backtest looks profitable.
