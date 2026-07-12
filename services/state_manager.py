"""
Responsibility: persist and load per-symbol strategy state.
Stores state ONLY (no candle values) so the bot can recover after a restart
without re-bootstrapping every symbol from scratch, per the spec's
"Startup Logic" (state is loaded if present; only unseen symbols get a
fresh bootstrap replay).

Backing store: data/symbol_states.csv
Columns: Symbol, State, Direction, Last Alert, Updated
(extra internal fields needed to resume the state machine — retracement
flag, extreme price tracker, last processed candle time — are persisted
in the same row so recovery is exact, not just approximate.)
"""
import csv
from datetime import datetime, timezone
from threading import Lock

from config import settings
from strategy.strategy import SymbolState

_lock = Lock()

FIELDNAMES = [
    "Symbol", "State", "Direction", "RetracementStarted", "ExtremePrice",
    "LastProcessedTime", "LastAlert", "LastAlertPrice", "Updated",
]


def load_all() -> dict:
    """Load all persisted symbol states into {symbol: SymbolState}."""
    states = {}
    if not settings.STATES_CSV.exists():
        return states

    with open(settings.STATES_CSV, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row["Symbol"]
            states[symbol] = SymbolState(
                symbol=symbol,
                state=row.get("State") or "WAIT_CROSSOVER",
                direction=row.get("Direction") or None,
                retracement_started=(row.get("RetracementStarted") == "True"),
                extreme_price=_to_float_or_none(row.get("ExtremePrice")),
                last_processed_time=row.get("LastProcessedTime") or None,
                last_alert_time=row.get("LastAlert") or None,
                last_alert_price=_to_float_or_none(row.get("LastAlertPrice")),
            )
    return states


def save_all(states: dict):
    """Overwrite data/symbol_states.csv with the full current state set."""
    with _lock:
        with open(settings.STATES_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            now = datetime.now(timezone.utc).isoformat()
            for symbol, state in states.items():
                writer.writerow({
                    "Symbol": symbol,
                    "State": state.state,
                    "Direction": state.direction or "",
                    "RetracementStarted": state.retracement_started,
                    "ExtremePrice": "" if state.extreme_price is None else state.extreme_price,
                    "LastProcessedTime": state.last_processed_time or "",
                    "LastAlert": state.last_alert_time or "",
                    "LastAlertPrice": "" if state.last_alert_price is None else state.last_alert_price,
                    "Updated": now,
                })


def _to_float_or_none(v):
    if v is None or v == "":
        return None
    return float(v)
