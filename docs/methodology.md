# Methodology

## Architecture

The engine separates signal generation from execution and portfolio accounting. Strategies emit target weights. The portfolio converts targets to orders using current marked equity, the execution model converts orders to fills with commission, slippage, and spread costs, and the portfolio updates cash and inventory from fills.

## Look-ahead control

Signals are calculated only from data available through the prior bar. Orders are then executed on the current bar. This prevents a strategy from observing today's close and simultaneously receiving that same close as an executable fill.

The earlier same-close implementation produced materially different results, especially for mean reversion. Removing that timing advantage caused the apparent profitability to disappear, which is retained as part of the research lesson.

## Exposure control

Target weights are normalized to a maximum gross exposure. Because prices can move between rebalances, marked gross exposure is checked on every bar. If it drifts beyond the configured risk limit, positions are proportionally deleveraged.

## Momentum

The momentum signal ranks medium-term price performance across the ETF universe and converts standardized scores into market-neutral target weights. Multiple lookbacks are reported rather than selecting the best historical result.

## Mean reversion

The mean-reversion strategy standardizes each asset's latest return against its own recent return distribution and takes the opposite exposure. High turnover makes implementation costs particularly important.

## Pairs / statistical arbitrage

The pairs model estimates a rolling hedge ratio in log-price space. A trade is permitted only when:

- the pair passes a rolling Engle-Granger cointegration screen,
- the estimated spread passes an ADF stationarity screen,
- the spread z-score breaches an entry threshold.

Positions close when the spread mean-reverts toward the exit threshold, the signal reverses, or the maximum holding period is reached. Dollar gross exposure is normalized after applying the hedge ratio.

## Walk-forward validation

Chronological training and test windows are used for all three strategies. The training slice is supplied only as signal-history warmup. Cash and positions remain untouched until the first OOS date, so reported OOS P&L and trade diagnostics contain no in-sample trading activity.

## Cost sensitivity

Each strategy is re-run under aggregate implementation-cost assumptions from 0 to 5 bps per transaction event. This distinguishes strategies with weak underlying signals from strategies whose returns are primarily eroded by implementation friction.

## Parameter robustness

Momentum, mean-reversion, and pairs lookbacks are evaluated over small, economically reasonable parameter neighborhoods. These runs are reported as robustness diagnostics rather than used to choose a historical winner.

## Benchmark

SPY buy-and-hold provides a simple opportunity-cost benchmark. The objective is not to force market-neutral strategies to beat SPY mechanically, but to make the risk/return trade-off visible.

## Interpretation

The final live run finds no robust alpha in the tested momentum or mean-reversion specifications. The filtered pairs strategy exhibits lower turnover and drawdown but negligible economic return. These negative findings are considered valid research outcomes rather than model failures.
