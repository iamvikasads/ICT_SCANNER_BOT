import os
import time
import logging
from datetime import datetime, timedelta,UTC

from core.binance.client import BinanceClient
from core.binance.downloader import OHLCVDownloader

from scanner.strategy1_scanner import Strategy1Scanner
from scanner.strategy1_entry_scanner import Strategy1EntryScanner
from scanner.strategy2_scanner import Strategy2Scanner
from scanner.strategy2_entry_scanner import Strategy2EntryScanner
from scanner.strategy3_scanner import Strategy3Scanner
from scanner.strategy3_entry_scanner import Strategy3EntryScanner

from services.trade_tracker import TradeTracker
from services.daily_summary import DailySummary

from alerts.telegram_client import TelegramClient
from core.logger import logger


# ===================================
# SETTINGS
# ===================================

LOG_SCANNER_OUTPUT = True


# ===================================
# HELPERS
# ===================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def now_utc():
    return datetime.now(UTC).replace(tzinfo=None)


def print_next_scan():

    now = datetime.now(UTC).replace(tzinfo=None)

    next_scan = (
        now.replace(
            minute=0,
            second=0,
            microsecond=0
        )
        + timedelta(hours=1)
    )

    next_scan_ist = next_scan + timedelta(
        hours=5,
        minutes=30
    )

    print(
        f"\nNext Scan: "
        f"{next_scan_ist.strftime('%H:%M')} IST\n"
    )

# ===================================
# INITIALIZE — inside try/except
# so startup failures are reported
# ===================================

telegram = TelegramClient()

try:
    # ONE shared BinanceClient and OHLCVDownloader
    # All scanners use the same instance — avoids duplicate API connections
    shared_client = BinanceClient()
    shared_downloader = OHLCVDownloader(client=shared_client)

    strategy1 = Strategy1Scanner(downloader=shared_downloader)
    strategy1_entry = Strategy1EntryScanner(downloader=shared_downloader)

    strategy2 = Strategy2Scanner(downloader=shared_downloader)
    strategy2_entry = Strategy2EntryScanner(downloader=shared_downloader)

    strategy3 = Strategy3Scanner(downloader=shared_downloader)
    strategy3_entry = Strategy3EntryScanner(downloader=shared_downloader)

    tracker = TradeTracker(downloader=shared_downloader)
    summary = DailySummary()

except Exception as init_err:
    logger.error(f"STARTUP FAILED: {init_err}")
    telegram.send_message(f"🚨 ICT BOT STARTUP FAILED\n\n{init_err}")
    raise SystemExit(1)


# ===================================
# STARTUP
# ===================================

clear_screen()
logger.info("ICT SCANNER BOT STARTED")

telegram.send_message(
    "🟢 ICT SCANNER BOT STARTED \n\n"
    
)

print_next_scan()

last_run_slot = None
last_summary_date = None
error_count = 0
setups_found_today = 0
entries_fired_today = 0


# ===================================
# MAIN LOOP
# ===================================

while True:

    try:

        now = now_utc()
        minute = now.minute
        current_hour_slot = now.strftime("%Y%m%d%H")
        today_date = now.strftime("%Y%m%d")

        # ===================================
        # DAILY SUMMARY at 00:00 UTC
        # ===================================

        if now.hour == 0 and now.minute < 2 and last_summary_date != today_date:
            try:
                summary.send(
                    setups_found=setups_found_today,
                    entries_fired=entries_fired_today,
                    errors=error_count
                )
                last_summary_date = today_date
                setups_found_today = 0
                entries_fired_today = 0
                error_count = 0
                logger.info("Daily summary sent")
            except Exception as e:
                logger.error(f"Summary error: {e}")

        # ===================================
        # RUN SCANNERS AT :05 past the hour
        # (4H candles close on the hour, :05
        #  ensures they're confirmed on Binance)
        # ===================================

        if minute == 0 and last_run_slot != current_hour_slot:

            clear_screen()
            logger.info(f"=== SCAN START {now.strftime('%H:%M UTC')} ===")

            # FIX: Clear per-run cache so each new scan gets fresh data
            shared_downloader.clear_cache()

            # ======================
            # STRATEGY 1
            # ======================

            print(f"\n{now.strftime('%H:%M')} RUNNING STRATEGY 1")
            logger.info("Strategy 1 scan start")

            try:
                strategy1.run()
                strategy1_entry.run()
            except Exception as e:
                error_count += 1
                logger.error(f"Strategy 1 error: {e}")
                telegram.send_message(f"⚠️ S1 ERROR\n{e}")

            shared_downloader.clear_cache()

            # ======================
            # STRATEGY 2
            # ======================

            print(f"\n{now.strftime('%H:%M')} RUNNING STRATEGY 2")
            logger.info("Strategy 2 scan start")

            try:
                strategy2.run()
                strategy2_entry.run()
            except Exception as e:
                error_count += 1
                logger.error(f"Strategy 2 error: {e}")
                telegram.send_message(f"⚠️ S2 ERROR\n{e}")

            shared_downloader.clear_cache()

            # ======================
            # STRATEGY 3
            # ======================

            print(f"\n{now.strftime('%H:%M')} RUNNING STRATEGY 3")
            logger.info("Strategy 3 scan start")

            try:
                strategy3.run()
                strategy3_entry.run()
            except Exception as e:
                error_count += 1
                logger.error(f"Strategy 3 error: {e}")
                telegram.send_message(f"⚠️ S3 ERROR\n{e}")

            shared_downloader.clear_cache()

            # ======================
            # TRADE TRACKER
            # ======================

            print(f"\n{now.strftime('%H:%M')} RUNNING TRADE TRACKER")
            logger.info("Trade tracker start")

            try:
                tracker.run()
            except Exception as e:
                error_count += 1
                logger.error(f"Tracker error: {e}")
                telegram.send_message(f"⚠️ TRACKER ERROR\n{e}")

            last_run_slot = current_hour_slot
            logger.info("=== SCAN COMPLETE ===")
            print_next_scan()

        time.sleep(10)

    except KeyboardInterrupt:

        telegram.send_message(
            "🔴 ICT SCANNER BOT STOPPED\n\nStopped manually."
        )
        logger.info("Bot stopped by user")
        print("\nBOT STOPPED BY USER\n")
        break

    except Exception as e:

        error_count += 1
        logger.error(f"Main loop error: {e}")
        telegram.send_message(f"🚨 ICT SCANNER ERROR\n\n{e}")
        time.sleep(10)