"""
Single strategy file implementing the EMA9/EMA35 cross + retracement +
confirmation state machine, for both LONG and SHORT, per the spec:

WAIT_CROSSOVER -> WAIT_RETRACEMENT -> WAIT_CONFIRMATION -> ALERT_SENT -> WAIT_CROSSOVER

Internally WAIT_RETRACEMENT and WAIT_CONFIRMATION are tracked as one state
("WAIT_RETRACEMENT") with a `retracement_started` flag, since confirmation
is just the second half of the retracement phase (tracking the last
red/green candle and watching for the break candle). This keeps a single
source of truth for "have we started watching for the break" without
duplicating the invalidation logic.

This module is pure logic: given the current persisted state for a symbol
and a DataFrame with EMA_FAST/EMA_SLOW already computed, it advances the
state machine over any new (not yet processed) closed candles and returns
the updated state plus any signal(s) generated.
"""
from dataclasses import dataclass, asdict, field
from typing import Optional

import pandas as pd

from config import settings
from indicators import ema
from core.logger import get_logger

log = get_logger(__name__)

STATE_WAIT_CROSSOVER = "WAIT_CROSSOVER"
STATE_WAIT_RETRACEMENT = "WAIT_RETRACEMENT"
STATE_ALERT_SENT = "ALERT_SENT"

LONG = "LONG"
SHORT = "SHORT"


@dataclass
class SymbolState:
    symbol: str
    state: str = STATE_WAIT_CROSSOVER
    direction: Optional[str] = None
    retracement_started: bool = False
    extreme_price: Optional[float] = None   # last red high (LONG) / last green low (SHORT)
    last_processed_time: Optional[str] = None  # ISO timestamp of last candle we evaluated
    last_alert_time: Optional[str] = None
    last_alert_price: Optional[float] = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**{k: d.get(k) for k in cls.__dataclass_fields__.keys()})


def _reset(state: SymbolState):
    state.state = STATE_WAIT_CROSSOVER
    state.direction = None
    state.retracement_started = False
    state.extreme_price = None


def _process_one_candle(state: SymbolState, df: pd.DataFrame, idx: int):
    """
    Advance the state machine by exactly one closed candle (row `idx` of df).
    Returns a signal dict if a LONG/SHORT alert fires on this candle, else None.
    """
    if idx == 0:
        return None  # need a previous candle to detect a cross

    prev_fast, prev_slow = df.loc[idx - 1, "EMA_FAST"], df.loc[idx - 1, "EMA_SLOW"]
    curr_fast, curr_slow = df.loc[idx, "EMA_FAST"], df.loc[idx, "EMA_SLOW"]

    bullish_cross = prev_fast <= prev_slow and curr_fast > curr_slow
    bearish_cross = prev_fast >= prev_slow and curr_fast < curr_slow

    curr_close = df.loc[idx, "Close"]
    curr_open = df.loc[idx, "Open"]
    curr_high = df.loc[idx, "High"]
    curr_low = df.loc[idx, "Low"]
    is_red = curr_close < curr_open
    is_green = curr_close > curr_open

    # ---------------------------------------------------------------
    # ALERT_SENT: ignore everything until the opposite cross, then reset
    # ---------------------------------------------------------------
    if state.state == STATE_ALERT_SENT:
        if state.direction == LONG and bearish_cross:
            _reset(state)
        elif state.direction == SHORT and bullish_cross:
            _reset(state)
        return None

    # ---------------------------------------------------------------
    # WAIT_CROSSOVER: look for a fresh, qualified EMA cross
    # ---------------------------------------------------------------
    if state.state == STATE_WAIT_CROSSOVER:
        if bullish_cross:
            if ema.slope_up(df, idx) and ema.separation_pct(df, idx) >= settings.MIN_EMA_SEPARATION_PCT:
                state.state = STATE_WAIT_RETRACEMENT
                state.direction = LONG
                state.retracement_started = False
                state.extreme_price = None
        elif bearish_cross:
            if ema.slope_down(df, idx) and ema.separation_pct(df, idx) >= settings.MIN_EMA_SEPARATION_PCT:
                state.state = STATE_WAIT_RETRACEMENT
                state.direction = SHORT
                state.retracement_started = False
                state.extreme_price = None
        return None

    # ---------------------------------------------------------------
    # WAIT_RETRACEMENT (covers both "waiting for retracement to start"
    # and "confirmation" sub-phases)
    # ---------------------------------------------------------------
    if state.state == STATE_WAIT_RETRACEMENT:
        if state.direction == LONG:
            # A brand-new opposite cross always takes priority
            if bearish_cross:
                _reset(state)
                return None

            if not state.retracement_started:
                if curr_close < curr_fast:  # close < EMA9 -> retracement starts NOW
                    state.retracement_started = True
                else:
                    return None  # still waiting for retracement to start

            # Retracement active (this may be the very same candle that just
            # started it — that candle's color still counts for tracking).
            if curr_close < curr_slow:  # close < EMA35 -> cancel setup
                _reset(state)
                return None

            if is_red:
                state.extreme_price = curr_high if state.extreme_price is None else max(state.extreme_price, curr_high)
                return None

            if is_green and state.extreme_price is not None:
                body_ok = ema.body_size_pct(df, idx) >= settings.MIN_BODY_SIZE_PCT
                if curr_close > curr_fast and curr_close > state.extreme_price and body_ok:
                    state.state = STATE_ALERT_SENT
                    state.last_alert_time = str(df.loc[idx, "Time"])
                    state.last_alert_price = float(curr_close)
                    return {
                        "symbol": state.symbol,
                        "direction": LONG,
                        "price": float(curr_close),
                        "time": df.loc[idx, "Time"],
                    }
            return None

        else:  # SHORT — mirror image of LONG
            if bullish_cross:
                _reset(state)
                return None

            if not state.retracement_started:
                if curr_close > curr_fast:  # close > EMA9 -> retracement starts NOW
                    state.retracement_started = True
                else:
                    return None

            if curr_close > curr_slow:  # close > EMA35 -> cancel setup
                _reset(state)
                return None

            if is_green:
                state.extreme_price = curr_low if state.extreme_price is None else min(state.extreme_price, curr_low)
                return None

            if is_red and state.extreme_price is not None:
                body_ok = ema.body_size_pct(df, idx) >= settings.MIN_BODY_SIZE_PCT
                if curr_close < curr_fast and curr_close < state.extreme_price and body_ok:
                    state.state = STATE_ALERT_SENT
                    state.last_alert_time = str(df.loc[idx, "Time"])
                    state.last_alert_price = float(curr_close)
                    return {
                        "symbol": state.symbol,
                        "direction": SHORT,
                        "price": float(curr_close),
                        "time": df.loc[idx, "Time"],
                    }
            return None

    return None


def bootstrap_state(symbol: str, df: pd.DataFrame) -> SymbolState:
    """
    Replay the FULL candle history from scratch to determine the current
    state on cold start (per "Startup Logic" in the spec). No alerts are
    fired during bootstrap — we only want to know where we stand.
    """
    df = ema.add_emas(df)
    state = SymbolState(symbol=symbol)
    for idx in range(len(df)):
        _process_one_candle(state, df, idx)
    if len(df):
        state.last_processed_time = str(df.loc[len(df) - 1, "Time"])
    return state


def advance_state(state: SymbolState, df: pd.DataFrame) -> list[dict]:
    """
    Given a persisted state and a freshly downloaded candle window,
    process only the candles newer than `last_processed_time` (normally
    just the one candle that just closed). Returns a list of signal dicts
    (usually 0 or 1, but more if the bot missed several candle closes).
    """
    df = ema.add_emas(df)

    if state.last_processed_time is None:
        # First time we see this symbol without a prior bootstrap — bootstrap now.
        bootstrapped = bootstrap_state(state.symbol, df)
        state.__dict__.update(bootstrapped.__dict__)
        return []

    last_seen = pd.Timestamp(state.last_processed_time)
    new_rows = df.index[df["Time"] > last_seen].tolist()

    signals = []
    for idx in new_rows:
        signal = _process_one_candle(state, df, idx)
        state.last_processed_time = str(df.loc[idx, "Time"])
        if signal:
            signals.append(signal)

    return signals
