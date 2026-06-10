from datetime import datetime, timezone
from core.binance.client import BinanceClient


class OHLCVDownloader:

    def __init__(self, client=None):
        # Accept shared client or create own
        if client is not None:
            self.client = client
        else:
            self.client = BinanceClient()

        # Per-run cache: {(symbol, interval, limit): candles}
        self._cache = {}

    def clear_cache(self):
        self._cache = {}

    def get_ohlcv(self, symbol, interval, limit=500):

        cache_key = (symbol, interval, limit)

        if cache_key in self._cache:
            return self._cache[cache_key]

        data = self.client.client.futures_klines(
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        candles = []
        for row in data:
            candles.append({
                "timestamp": row[0],
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": float(row[5])
            })

        self._cache[cache_key] = candles
        return candles

    def get_previous_day_levels(self, symbol):

        # FIX: Fetch 3 candles, validate timestamp is before today midnight
        daily_candles = self.get_ohlcv(
            symbol=symbol,
            interval="1d",
            limit=3
        )

        today_midnight_utc = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_ts_ms = int(today_midnight_utc.timestamp() * 1000)

        # Walk backwards and find the first candle strictly before today
        previous_day = None
        for candle in reversed(daily_candles):
            if candle["timestamp"] < today_ts_ms:
                previous_day = candle
                break

        if previous_day is None:
            previous_day = daily_candles[-2]

        return {
            "pdh": previous_day["high"],
            "pdl": previous_day["low"]
        }
