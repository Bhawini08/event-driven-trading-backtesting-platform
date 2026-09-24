from dataclasses import dataclass
from .events import OrderEvent, FillEvent

@dataclass
class ExecutionModel:
    commission_bps: float = 0.5
    slippage_bps: float = 1.0
    half_spread_bps: float = 1.5

    def fill(self, order: OrderEvent, mid: float) -> FillEvent:
        side = 1.0 if order.quantity > 0 else -1.0
        spread = mid * self.half_spread_bps / 1e4
        slip = mid * self.slippage_bps / 1e4
        fill_price = mid + side * (spread + slip)
        notional = abs(order.quantity * fill_price)
        commission = notional * self.commission_bps / 1e4
        return FillEvent(order.timestamp, order.symbol, order.quantity, fill_price,
                         commission, abs(order.quantity) * slip,
                         abs(order.quantity) * spread, order.strategy)
