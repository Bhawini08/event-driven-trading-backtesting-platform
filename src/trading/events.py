from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class MarketEvent:
    timestamp: pd.Timestamp
    prices: dict[str, float]

@dataclass(frozen=True)
class SignalEvent:
    timestamp: pd.Timestamp
    symbol: str
    target_weight: float
    strategy: str

@dataclass(frozen=True)
class OrderEvent:
    timestamp: pd.Timestamp
    symbol: str
    quantity: float
    strategy: str

@dataclass(frozen=True)
class FillEvent:
    timestamp: pd.Timestamp
    symbol: str
    quantity: float
    price: float
    commission: float
    slippage_cost: float
    spread_cost: float
    strategy: str
