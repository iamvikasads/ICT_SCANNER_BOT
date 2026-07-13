"""
Responsibility: Send Telegram messages only.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from config import settings
from core.logger import get_logger

log = get_logger(__name__)

API_URL = "https://api.telegram.org/bot{token}/sendMessage"

IST = ZoneInfo("Asia/Kolkata")


def send_telegram_message(text: str) -> bool:
    """
    Send a plain text message to Telegram.
    """

    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        log.warning(
            "Telegram credentials not configured — skipping send.\n%s",
            text,
        )
        return False

    url = API_URL.format(token=settings.TELEGRAM_BOT_TOKEN)

    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": text,
    }

    try:
        response = requests.post(
            url,
            data=payload,
            timeout=10,
        )

        response.raise_for_status()

        return True

    except Exception as exc:
        log.error(f"Failed to send Telegram message: {exc}")
        return False


def send_startup_message(symbol_count: int, next_scan: str) -> bool:
    """
    Send bot startup notification.
    """

    now = datetime.now(IST).strftime("%d-%m-%Y %H:%M:%S")

    message = (
        "🟢 EMA ALERT BOT V1\n\n"
        "Status : ONLINE\n\n"
        "✅ Connected to Binance\n"
        f"✅ Symbols Loaded : {symbol_count}\n"
        "✅ Scheduler Started\n\n"
        "Timeframe : 4H\n"
        f"Started : {now} IST\n"
        f"Next Scan : {next_scan}\n\n"
        "Waiting for next 4H candle close..."
    )

    return send_telegram_message(message)


def send_shutdown_message() -> bool:
    """
    Send bot shutdown notification.
    """

    now = datetime.now(IST).strftime("%d-%m-%Y %H:%M:%S")

    message = (
        "🔴 EMA ALERT BOT V1\n\n"
        "Status : OFFLINE\n\n"
        f"Stopped : {now} IST\n\n"
        "Reason : Manual Stop"
    )

    return send_telegram_message(message)


def send_crash_message(error: Exception) -> bool:
    """
    Send bot crash notification.
    """

    now = datetime.now(IST).strftime("%d-%m-%Y %H:%M:%S")

    message = (
        "🚨 EMA ALERT BOT V1\n\n"
        "Status : CRASHED\n\n"
        f"Time : {now} IST\n\n"
        f"Error:\n{error}"
    )

    return send_telegram_message(message)


def send_scan_summary(
    scanned: int,
    alerts_sent: int,
    next_scan: str,
) -> bool:
    """
    Send scan completion summary.
    """

    now = datetime.now(IST).strftime("%d-%m-%Y %H:%M:%S")

    message = (
        "📊 SCAN COMPLETE\n\n"
        f"Time : {now} IST\n\n"
        f"Coins Scanned : {scanned}\n"
        f"📨 Alerts Sent : {alerts_sent}\n\n"
        f"Next Scan : {next_scan}"
    )

    return send_telegram_message(message)