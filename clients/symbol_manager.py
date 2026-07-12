"""
Responsibility:
  1. Download futures exchange info
  2. Filter USDT-M Perpetuals
  3. Sort by 24H quote volume
  4. Return the Top N symbols
"""
from clients.binance import get_client
from config import settings
from core.logger import get_logger

log = get_logger(__name__)


def get_top_n_symbols(n: int = None) -> list[str]:
    n = n or settings.TOP_N_SYMBOLS
    client = get_client()

    exchange_info = client.futures_exchange_info()
    perpetual_usdt_symbols = {
        s["symbol"]
        for s in exchange_info["symbols"]
        if s.get("contractType") == "PERPETUAL"
        and s.get("quoteAsset") == "USDT"
        and s.get("status") == "TRADING"
    }

    tickers = client.futures_ticker()  # 24hr ticker stats, all symbols
    filtered = [
        t for t in tickers
        if t["symbol"] in perpetual_usdt_symbols
    ]

    filtered.sort(key=lambda t: float(t.get("quoteVolume", 0.0)), reverse=True)

    top_symbols = [t["symbol"] for t in filtered[:n]]
    log.info(f"Loaded top {len(top_symbols)} USDT-M perpetual symbols by 24h quote volume.")
    return top_symbols
