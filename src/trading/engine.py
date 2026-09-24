from __future__ import annotations
import pandas as pd
from .portfolio import Portfolio
from .execution import ExecutionModel

class BacktestEngine:
    def __init__(self, prices: pd.DataFrame, strategy, initial_cash=1_000_000, rebalance_every=5,
                 execution: ExecutionModel|None=None, trading_start=None, max_gross=1.0):
        self.prices=prices.dropna().copy()
        self.strategy=strategy
        self.rebalance_every=rebalance_every
        self.portfolio=Portfolio(initial_cash)
        self.execution=execution or ExecutionModel()
        self.trading_start=pd.Timestamp(trading_start) if trading_start is not None else None
        self.max_gross=float(max_gross)

    def _execute_orders(self, orders, prices):
        for order in orders:
            self.portfolio.apply_fill(self.execution.fill(order,prices[order.symbol]))

    def _enforce_gross_cap(self, timestamp, prices):
        """Deleverage proportionally when marked gross exposure drifts above the cap.

        Targeting a small buffer below the hard cap accounts for execution costs reducing
        equity during the rebalance. The guard is applied every bar and after scheduled
        strategy rebalances.
        """
        for _ in range(3):
            gross=self.portfolio.gross_exposure()
            if gross <= self.max_gross*1.001:
                break
            eq=self.portfolio.equity()
            if eq <= 0:
                break
            target_gross=self.max_gross*0.99
            scale=target_gross/gross
            targets={}
            for symbol,qty in self.portfolio.positions.items():
                px=self.portfolio.last_prices.get(symbol)
                if px is None:
                    continue
                current_weight=qty*px/eq
                targets[symbol]=current_weight*scale
            orders=self.portfolio.orders_from_targets(
                timestamp,targets,self.strategy.name,self.max_gross
            )
            if not orders:
                break
            self._execute_orders(orders,prices)

    def run(self):
        rows=[]
        for i,(ts,row) in enumerate(self.prices.iterrows()):
            prices=row.to_dict()
            self.portfolio.mark(prices)
            can_trade=self.trading_start is None or ts>=self.trading_start

            # Mark-to-market can make gross exposure drift above the risk limit
            # even when prior target weights respected the cap.
            if can_trade:
                self._enforce_gross_cap(ts,prices)

            if can_trade and i % self.rebalance_every==0 and i>0:
                # Form the signal only from information through the prior bar,
                # then execute using the current bar.
                targets=self.strategy.targets(self.prices.iloc[:i])
                orders=self.portfolio.orders_from_targets(
                    ts,targets,self.strategy.name,self.max_gross
                )
                self._execute_orders(orders,prices)
                self._enforce_gross_cap(ts,prices)

            equity=self.portfolio.equity()
            rows.append({
                "timestamp":ts,
                "equity":equity,
                "pnl":equity-self.portfolio.initial_cash,
                "gross_exposure":self.portfolio.gross_exposure(),
                "net_exposure":self.portfolio.net_exposure(),
            })

        curve=pd.DataFrame(rows).set_index("timestamp")
        curve["period_pnl"]=curve["equity"].diff().fillna(
            curve["equity"].iloc[0]-self.portfolio.initial_cash
        )
        trades=pd.DataFrame(self.portfolio.trade_log)
        return curve,trades
