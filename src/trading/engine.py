from __future__ import annotations
import pandas as pd
from .portfolio import Portfolio
from .execution import ExecutionModel

class BacktestEngine:
    def __init__(self, prices: pd.DataFrame, strategy, initial_cash=1_000_000, rebalance_every=5,
                 execution: ExecutionModel|None=None):
        self.prices=prices.dropna().copy(); self.strategy=strategy; self.rebalance_every=rebalance_every
        self.portfolio=Portfolio(initial_cash); self.execution=execution or ExecutionModel()

    def run(self):
        rows=[]
        for i,(ts,row) in enumerate(self.prices.iterrows()):
            self.portfolio.mark(row.to_dict())
            if i % self.rebalance_every == 0:
                targets=self.strategy.targets(self.prices.iloc[:i+1])
                for order in self.portfolio.orders_from_targets(ts,targets,self.strategy.name):
                    self.portfolio.apply_fill(self.execution.fill(order,row[order.symbol]))
            rows.append({"timestamp":ts,"equity":self.portfolio.equity(),
                         "gross_exposure":self.portfolio.gross_exposure(),
                         "net_exposure":self.portfolio.net_exposure()})
        curve=pd.DataFrame(rows).set_index("timestamp")
        trades=pd.DataFrame(self.portfolio.trade_log)
        return curve,trades
