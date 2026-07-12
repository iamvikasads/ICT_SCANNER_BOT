"""
Responsibility: download candles and return a clean DataFrame.
Never calculates EMA or strategy logic here.
"""
import pandas as pd

from clients.binance import get_client
from core.logger import get_logger

log = get_logger(__name__)

COLUMNS = ["Time", "Open", "High", "Low", "Close", "Volume"]


def get_klines(symbol: str, interval: str, limit: int = 500) -> pd.DataFrame:
    """
    Download the latest `limit` closed candles for `symbol` at `interval`
    from Binance USDT-M Futures. Returns a DataFrame with columns:
    Time, Open, High, Low, Close, Volume (Time = candle open time, UTC).
    """
    client = get_client()

    raw = client.futures_klines(symbol=symbol, interval=interval, limit=limit + 1)

    # futures_klines returns the currently-forming candle as the last row.
    # Drop it so we only ever work with CLOSED candles.
    if raw:
        raw = raw[:-1]

    if not raw:
        log.warning(f"No kline data returned for {symbol}.")
        return pd.DataFrame(columns=COLUMNS)

    df = pd.DataFrame(raw, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore",
    ])

    df["Time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    for col_src, col_dst in [("open", "Open"), ("high", "High"),
                              ("low", "Low"), ("close", "Close"),
                              ("volume", "Volume")]:
        df[col_dst] = df[col_src].astype(float)

    df = df[COLUMNS].reset_index(drop=True)
    return df
