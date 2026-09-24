from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd
from .events import FillEvent, OrderEvent

@dataclass
class Portfolio:
    initial_cash: float = 1_000_000.0
    cash: float = field(init=False)
    positions: dict[str, float] = field(default_factory=dict)
    last_prices: dict[str, float] = field(default_factory=dict)
    trade_log: list[dict] = field(default_factory=list)

    def __post_init__(self):
        self.cash = float(self.initial_cash)

    def equity(self) -> float:
        return self.cash + sum(q * self.last_prices.get(s, 0.0) for s, q in self.positions.items())

    def mark(self, prices: dict[str, float]) -> None:
        self.last_prices.update(prices)

    def gross_exposure(self) -> float:
        eq = self.equity()
        if eq == 0: return 0.0
        return sum(abs(q*self.last_prices.get(s,0.0)) for s,q in self.positions.items()) / eq

    def net_exposure(self) -> float:
        eq = self.equity()
        if eq == 0: return 0.0
        return sum(q*self.last_prices.get(s,0.0) for s,q in self.positions.items()) / eq

    def orders_from_targets(self, timestamp: pd.Timestamp, targets: dict[str,float], strategy: str) -> list[OrderEvent]:
        eq = self.equity()
        orders=[]
        for s,w in targets.items():
            px=self.last_prices[s]
            desired = eq*w/px
            qty = desired-self.positions.get(s,0.0)
            if abs(qty) > 1e-8:
                orders.append(OrderEvent(timestamp,s,qty,strategy))
        return orders

    def apply_fill(self, fill: FillEvent) -> None:
        self.cash -= fill.quantity*fill.price + fill.commission
        self.positions[fill.symbol] = self.positions.get(fill.symbol,0.0)+fill.quantity
        self.trade_log.append(fill.__dict__.copy())
