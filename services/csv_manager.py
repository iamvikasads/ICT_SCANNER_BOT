"""
Responsibility: append-only CSV persistence for alerts.
(Per-symbol state persistence lives in services/state_manager.py.)
"""
import csv
from datetime import datetime, timezone

from config import settings

ALERTS_HEADER = ["Date", "Coin", "Direction", "Price", "Message"]


def _ensure_header(path, header):
    if not path.exists():
        with open(path, "w", newline="") as f:
            csv.writer(f).writerow(header)


def save_alert(symbol: str, direction: str, price: float, message: str):
    _ensure_header(settings.ALERTS_CSV, ALERTS_HEADER)
    with open(settings.ALERTS_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now(timezone.utc).isoformat(),
            symbol,
            direction,
            f"{price:.8f}".rstrip("0").rstrip("."),
            message.replace("\n", " | "),
        ])
