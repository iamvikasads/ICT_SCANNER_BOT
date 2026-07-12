"""
Responsibility: turn a raw signal dict into the Telegram message text.
"""
from config import settings


def format_alert(signal: dict) -> str:
    direction = signal["direction"]
    emoji = "🟢" if direction == "LONG" else "🔴"
    symbol = signal["symbol"]
    price = signal["price"]
    time = signal["time"]

    return (
        f"{emoji} {direction} SETUP\n\n"
        f"Coin: {symbol}\n"
        f"Timeframe: {settings.TIMEFRAME.upper()}\n"
        f"EMA{settings.EMA_FAST} {'>' if direction == 'LONG' else '<'} EMA{settings.EMA_SLOW}\n"
        f"Retracement Confirmed\n"
        f"Confirmation Candle Closed: {time}\n"
        f"Price: {price}"
    )
