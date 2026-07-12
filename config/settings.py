"""
Central configuration. Everything is loaded from environment variables (.env)
with sane defaults so the bot can run out of the box for testing.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

ALERTS_CSV = DATA_DIR / "alerts.csv"
STATES_CSV = DATA_DIR / "symbol_states.csv"
LOG_FILE = LOGS_DIR / "bot.log"

# ---------------------------------------------------------------------------
# Binance
# ---------------------------------------------------------------------------
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")

# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ---------------------------------------------------------------------------
# Market / scan parameters
# ---------------------------------------------------------------------------
TIMEFRAME = os.getenv("TIMEFRAME", "4h")
CANDLE_LIMIT = int(os.getenv("CANDLE_LIMIT", "500"))
TOP_N_SYMBOLS = int(os.getenv("TOP_N_SYMBOLS", "100"))
SYMBOL_REFRESH_EVERY = int(os.getenv("SYMBOL_REFRESH_EVERY", "6"))

# ---------------------------------------------------------------------------
# Strategy parameters
# ---------------------------------------------------------------------------
EMA_FAST = int(os.getenv("EMA_FAST", "9"))
EMA_SLOW = int(os.getenv("EMA_SLOW", "35"))
SLOPE_LOOKBACK = int(os.getenv("SLOPE_LOOKBACK", "3"))
MIN_EMA_SEPARATION_PCT = float(os.getenv("MIN_EMA_SEPARATION_PCT", "0.3"))
MIN_BODY_SIZE_PCT = float(os.getenv("MIN_BODY_SIZE_PCT", "0.1"))

# Timeframe -> seconds, used by the scanner to sleep until the next close
TIMEFRAME_SECONDS = {
    "1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800,
    "1h": 3600, "2h": 7200, "4h": 14400, "6h": 21600, "8h": 28800,
    "12h": 43200, "1d": 86400,
}
