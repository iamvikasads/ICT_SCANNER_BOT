# EMA ALERT BOT V1

Scans the Top-N Binance USDT-M Perpetual Futures on a fixed timeframe (default 4H)
and sends a Telegram alert when the EMA9/EMA35 cross + retracement + confirmation
strategy fires. **Alert-only — no auto trading, no SL, no TP, no trade management.**

## Setup

```bash
cd EMA_ALERT_BOT
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: BINANCE_API_KEY/SECRET (read-only key is enough), TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
```

## Run

```bash
python3 main.py
```

The bot will:
1. Load the Top-N USDT-M perpetuals by 24h quote volume.
2. Load any previously persisted per-symbol state from `data/symbol_states.csv`
   (any symbol with no saved state gets bootstrapped by replaying its last 500
   closed candles once, silently, per the spec's Startup Logic — no alert is
   fired on that first pass).
3. Sleep until the next `TIMEFRAME` candle close (UTC-epoch aligned — never
   scans a forming candle).
4. On each close: download the latest closed candles per symbol, advance each
   symbol's state machine by exactly the new closed candle(s), send a Telegram
   alert + append to `data/alerts.csv` for any LONG/SHORT signal, then persist
   all states back to `data/symbol_states.csv`.
5. Repeat forever.

## Strategy state machine

```
WAIT_CROSSOVER -> WAIT_RETRACEMENT -> ALERT_SENT -> WAIT_CROSSOVER
```

- **WAIT_CROSSOVER**: watching for an EMA9/EMA35 cross. A cross only qualifies
  (moves to WAIT_RETRACEMENT) if EMA35 is sloping in the trend's direction
  (`SLOPE_LOOKBACK` candles back) and the EMA9/EMA35 separation is at least
  `MIN_EMA_SEPARATION_PCT`.
- **WAIT_RETRACEMENT**: waiting for price to pull back to EMA9, then tracking
  the retracement candle-by-candle (last red high for LONG / last green low
  for SHORT) until a break candle confirms (closes back through EMA9 *and*
  through the tracked extreme, with a body size ≥ `MIN_BODY_SIZE_PCT`) — or
  the retracement is invalidated by a close through EMA35, which cancels the
  setup and returns to WAIT_CROSSOVER. An opposite-direction cross at any
  point also cancels immediately.
- **ALERT_SENT**: everything is ignored until the opposite EMA cross occurs,
  at which point the state resets to WAIT_CROSSOVER (per spec Step 9).

All thresholds (`MIN_EMA_SEPARATION_PCT`, `MIN_BODY_SIZE_PCT`, `SLOPE_LOOKBACK`)
are in `.env` — the spec explicitly leaves these to be tuned after testing.

## Files

See the module docstrings — each file has exactly one responsibility, matching
the architecture doc (Binance client never calculates EMA, EMA module never
touches strategy logic, CSV/state managers only persist, etc).

## Known limitation in this environment

This bot was built and unit-tested against synthetic candle data (the state
machine's LONG/SHORT/reset/persistence paths are all verified). It has **not**
been run against live Binance data here, since this sandbox's network egress
doesn't include Binance's API domains — you'll need to run it from your own
server/VPS (same as your other bot) to validate against real market data.
