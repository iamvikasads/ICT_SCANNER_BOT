"""
Responsibility: orchestrate one full scan cycle across all symbols, and
sleep between cycles so the bot only ever scans right after a candle close
— never a live/forming candle.
"""
import os
import time
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import gc

from config import settings
from clients.market_data import get_klines
from clients.symbol_manager import get_top_n_symbols
from strategy.strategy import SymbolState, bootstrap_state, advance_state
from services import state_manager, csv_manager
from alerts.formatter import format_alert
from alerts.telegram import (
    send_telegram_message,
    send_startup_message,
    send_scan_summary,
)
from core.logger import get_logger

log = get_logger(__name__)

IST = ZoneInfo("Asia/Kolkata")
BOT_VERSION = "1.0.0"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def seconds_until_next_close(timeframe: str) -> float:
    """
    Seconds remaining until the next candle close boundary for `timeframe`,
    aligned to UTC epoch (Binance candle boundaries are epoch-aligned).
    """
    tf_seconds = settings.TIMEFRAME_SECONDS[timeframe]
    now = datetime.now(timezone.utc).timestamp()
    remainder = now % tf_seconds
    remaining = tf_seconds - remainder
    # small buffer so we don't race Binance finalizing the candle
    return remaining + 2


def scan_once(symbols: list[str], states: dict) -> int:
    """Run a single scan pass over all symbols. Returns number of alerts sent."""
    alerts_sent = 0

    for symbol in symbols:
        try:
            df = get_klines(symbol, settings.TIMEFRAME, settings.CANDLE_LIMIT)
            if df.empty or len(df) < settings.EMA_SLOW + settings.SLOPE_LOOKBACK + 1:
                log.warning(f"{symbol}: not enough candle data, skipping.")
                continue

            state = states.get(symbol)
            if state is None:
                state = bootstrap_state(symbol, df)
                states[symbol] = state
                log.info(f"{symbol}: bootstrapped -> state={state.state}, direction={state.direction}")
                continue  # don't fire alerts on the very first sight of a symbol

            signals = advance_state(state, df)

            for signal in signals:
                message = format_alert(signal)
                send_telegram_message(message)
                csv_manager.save_alert(
                    symbol=signal["symbol"],
                    direction=signal["direction"],
                    price=signal["price"],
                    message=message,
                )
                alerts_sent += 1
                log.info(f"ALERT: {signal['symbol']} {signal['direction']} @ {signal['price']}")

        except Exception as exc:
            log.exception(f"{symbol}: error during scan — {exc}")
            continue

    state_manager.save_all(states)
    return alerts_sent


def run_forever():
    log.info("EMA Alert Bot starting up.")
    BOT_START_TIME = datetime.now(IST)

    try:
        symbols = get_top_n_symbols()
        states = state_manager.load_all()

        log.info(
            f"Loaded {len(states)} persisted symbol states. "
            f"Scanning {len(symbols)} symbols."
        )

        next_scan = (
            datetime.now(timezone.utc)
            + timedelta(seconds=seconds_until_next_close(settings.TIMEFRAME))
        )

        next_scan_ist = next_scan.astimezone(IST).strftime("%H:%M:%S IST")

        send_startup_message(
            symbol_count=len(symbols),
            next_scan=next_scan_ist,
        )
    except Exception:
        raise

    log.info("=" * 60)
    log.info(f"EMA ALERT BOT V{BOT_VERSION}")
    log.info(f"Timeframe : {settings.TIMEFRAME}")
    log.info(f"Symbols   : {len(symbols)}")
    log.info(f"Next Scan : {next_scan_ist}")
    log.info("=" * 60)

    cycle = 0
    while True:
        sleep_for = seconds_until_next_close(settings.TIMEFRAME)
        current_time = datetime.now(IST).strftime("%H:%M:%S IST")
        next_scan = (
            datetime.now(timezone.utc)
            + timedelta(seconds=sleep_for)
        )
        next_scan_ist = next_scan.astimezone(IST).strftime("%H:%M:%S IST")
        hours = int(sleep_for // 3600)
        minutes = int((sleep_for % 3600) // 60)
        seconds = int(sleep_for % 60)
        log.info("=" * 60)
        log.info("WAITING FOR NEXT 4H CANDLE")
        log.info(f"Current Time : {current_time}")
        log.info(f"Next Scan    : {next_scan_ist}")
        log.info(f"Remaining    : {hours:02}:{minutes:02}:{seconds:02}")
        log.info("=" * 60)

        time.sleep(sleep_for)

        # Refresh the symbol universe periodically (volume ranks drift over time)
        if cycle > 0 and cycle % settings.SYMBOL_REFRESH_EVERY == 0:
            try:
                symbols = get_top_n_symbols()
            except Exception as exc:
                log.error(f"Failed to refresh symbol list, reusing previous list: {exc}")

        clear_screen()
        gc.collect()
        log.info("=" * 60)
        log.info("AUTO CLEAR COMPLETE")
        log.info("=" * 60)
        
        log.info(f"Scan cycle {cycle} starting for {len(symbols)} symbols.")
        
        start = time.time()
        alerts = scan_once(symbols, states)
        duration = round(time.time() - start, 2)
        
        log.info("=" * 60)
        log.info("SCAN COMPLETE")
        log.info(f"Coins Scanned : {len(symbols)}")
        log.info(f"Alerts Sent   : {alerts}")
        log.info(f"Duration      : {duration:.2f} sec")
        log.info(f"Next Scan     : {next_scan_ist}")
        log.info("=" * 60)

        if alerts > 0:
            send_scan_summary(
                scanned=len(symbols),
                alerts_sent=alerts,
                next_scan=next_scan_ist,
            )

        cycle += 1
        
        gc.collect()
        log.info("=" * 60)
        log.info("Memory Cleanup Completed")
        log.info("=" * 60)