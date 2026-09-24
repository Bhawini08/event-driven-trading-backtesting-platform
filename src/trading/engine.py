from __future__ import annotations
import pandas as pd
from .portfolio import Portfolio
from .execution import ExecutionModel

class BacktestEngine:
    def __init__(self, prices: pd.DataFrame, strategy, initial_cash=1_000_000, rebalance_every=5,
                 execution: ExecutionModel|None=None, trading_start=None):
        self.prices=prices.dropna().copy(); self.strategy=strategy; self.rebalance_every=rebalance_every
        self.portfolio=Portfolio(initial_cash); self.execution=execution or ExecutionModel()
        self.trading_start = pd.Timestamp(trading_start) if trading_start is not None else None

    def run(self):
        rows=[]
        for i,(ts,row) in enumerate(self.prices.iterrows()):
            self.portfolio.mark(row.to_dict())
            can_trade = self.trading_start is None or ts >= self.trading_start
            if can_trade and i % self.rebalance_every == 0:
                targets=self.strategy.targets(self.prices.iloc[:i+1])
                for order in self.portfolio.orders_from_targets(ts,targets,self.strategy.name):
                    self.portfolio.apply_fill(self.execution.fill(order,row[order.symbol]))
            equity=self.portfolio.equity()
            rows.append({"timestamp":ts,"equity":equity,
                         "pnl":equity-self.portfolio.initial_cash,
                         "gross_exposure":self.portfolio.gross_exposure(),
                         "net_exposure":self.portfolio.net_exposure()})
        curve=pd.DataFrame(rows).set_index("timestamp")
        curve["period_pnl"]=curve["equity"].diff().fillna(curve["equity"].iloc[0]-self.portfolio.initial_cash)
        trades=pd.DataFrame(self.portfolio.trade_log)
        return curve,trades
