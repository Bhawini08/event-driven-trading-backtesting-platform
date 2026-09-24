# Methodology

The engine deliberately separates signal generation from execution and portfolio accounting. Strategies emit target weights. The portfolio converts targets to orders using current marked equity, the execution model converts orders to fills with commission, slippage, and half-spread costs, and the portfolio updates cash and inventory from fills.

Walk-forward evaluation uses chronological training and test windows. A warm-up history is supplied for signal formation, but reported OOS statistics are calculated only on the test interval. Synthetic mode exists solely as a deterministic engineering fixture.

Cost sensitivity varies aggregate implementation friction and re-runs the same strategy. This is intended to expose fragile strategies whose performance disappears under modest execution assumptions.
