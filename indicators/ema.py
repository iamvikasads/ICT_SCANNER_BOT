"""
Responsibility: EMA9 / EMA35 calculation + slope + separation helpers.
Nothing else — no strategy logic here.
"""
import pandas as pd

from config import settings


def add_emas(df: pd.DataFrame,
             fast: int = None,
             slow: int = None) -> pd.DataFrame:
    """Adds EMA_FAST and EMA_SLOW columns to a copy of df and returns it."""
    fast = fast or settings.EMA_FAST
    slow = slow or settings.EMA_SLOW

    out = df.copy()
    out["EMA_FAST"] = out["Close"].ewm(span=fast, adjust=False).mean()
    out["EMA_SLOW"] = out["Close"].ewm(span=slow, adjust=False).mean()
    return out


def slope_up(df: pd.DataFrame, idx: int, lookback: int = None) -> bool:
    """True if EMA_SLOW at idx > EMA_SLOW `lookback` candles earlier."""
    lookback = lookback or settings.SLOPE_LOOKBACK
    if idx - lookback < 0:
        return False
    return df.loc[idx, "EMA_SLOW"] > df.loc[idx - lookback, "EMA_SLOW"]


def slope_down(df: pd.DataFrame, idx: int, lookback: int = None) -> bool:
    """True if EMA_SLOW at idx < EMA_SLOW `lookback` candles earlier."""
    lookback = lookback or settings.SLOPE_LOOKBACK
    if idx - lookback < 0:
        return False
    return df.loc[idx, "EMA_SLOW"] < df.loc[idx - lookback, "EMA_SLOW"]


def separation_pct(df: pd.DataFrame, idx: int) -> float:
    """Absolute % separation between EMA_FAST and EMA_SLOW at idx."""
    fast = df.loc[idx, "EMA_FAST"]
    slow = df.loc[idx, "EMA_SLOW"]
    if slow == 0:
        return 0.0
    return abs(fast - slow) / abs(slow) * 100.0


def body_size_pct(df: pd.DataFrame, idx: int) -> float:
    """% body size of the candle at idx, relative to its open price."""
    o = df.loc[idx, "Open"]
    c = df.loc[idx, "Close"]
    if o == 0:
        return 0.0
    return abs(c - o) / abs(o) * 100.0
