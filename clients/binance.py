"""
Thin wrapper around the Binance Futures client.
Responsibility: connect + verify. NEVER calculates EMA or strategy logic here.
"""
from binance.client import Client

from config import settings
from core.logger import get_logger

log = get_logger(__name__)

_client = None


def get_client() -> Client:
    """Return a singleton Binance Client, creating + verifying it on first call."""
    global _client
    if _client is not None:
        return _client

    client = Client(settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET)

    # Verify connectivity to the Futures API
    try:
        client.futures_ping()
        log.info("Connected to Binance Futures API.")
    except Exception as exc:
        log.error(f"Failed to connect to Binance Futures API: {exc}")
        raise

    _client = client
    return _client
