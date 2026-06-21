import os
import time
import logging
from datetime import datetime, timedelta, UTC

from core.binance.client import BinanceClient
from core.binance.downloader import OHLCVDownloader

from scanner.strategy1_scanner import Strategy1Scanner
from scanner.strategy1_entry_scanner import Strategy1EntryScanner

# Updated to V4 imports
from scanner.strategy2_scanner_v4 import Strategy2Scanner
from scanner.strategy2_entry_scanner_v4 import Strategy2EntryScanner

from scanner.strategy3_scanner_v4 import Strategy3Scanner
from scanner.strategy3_entry_scanner_v4 import Strategy3EntryScanner

from scanner.strategy4_scanner import Strategy4Scanner
from scanner.strategy4_mss_scanner import Strategy4MSSScanner
from scanner.strategy4_liquidity_scanner import Strategy4LiquidityScanner
from scanner.strategy4_entry_scanner import Strategy4EntryScanner

from services.trade_tracker import TradeTracker
from services.daily_summary import DailySummary

from alerts.discord_client import DiscordClient
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

    if now.minute < 2:

        next_scan = now.replace(
            minute=2,
            second=0,
            microsecond=0
        )

    elif now.minute < 32:

        next_scan = now.replace(
            minute=32,
            second=0,
            microsecond=0
        )

    else:

        next_scan = (
            now.replace(
                minute=2,
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

discord = DiscordClient()

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

    strategy4 = Strategy4Scanner(
        downloader=shared_downloader
    )

    strategy4_mss = Strategy4MSSScanner(
        downloader=shared_downloader
    )

    strategy4_liquidity = Strategy4LiquidityScanner(
        downloader=shared_downloader
    )

    strategy4_entry = Strategy4EntryScanner()

    tracker = TradeTracker(downloader=shared_downloader)
    summary = DailySummary()

except Exception as init_err:
    logger.error(f"STARTUP FAILED: {init_err}")
    discord.send_error(f"🚨 ICT BOT STARTUP FAILED\n\n{init_err}")
    raise SystemExit(1)


# ===================================
# STARTUP
# ===================================

clear_screen()
logger.info("ICT SCANNER BOT STARTED")

discord.send_status(
    "🟢 ICT SCANNER BOT STARTED"
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
        current_slot = now.strftime("%Y%m%d%H%M")
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

        if minute in [2, 32] and last_run_slot != current_slot:

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

                logger.error(
                    f"Strategy 1 error: {e}"
                )

                discord.send_error(
                    f"⚠️ S1 ERROR\n{e}"
                )

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

                logger.error(
                    f"Strategy 2 error: {e}"
                )

                discord.send_error(
                    f"⚠️ S2 ERROR\n{e}"
                )

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

                logger.error(
                    f"Strategy 3 error: {e}"
                )

                discord.send_error(
                    f"⚠️ S3 ERROR\n{e}"
                )

            shared_downloader.clear_cache()

            # ======================
            # STRATEGY 4
            # ======================

            print(f"\n{now.strftime('%H:%M')} RUNNING STRATEGY 4")
            logger.info("Strategy 4 scan start")

            try:

                strategy4.run()

                strategy4_mss.run()

                strategy4_liquidity.run()

                strategy4_entry.run()

            except Exception as e:

                error_count += 1

                logger.error(
                    f"Strategy 4 error: {e}"
                )

                discord.send_error(
                    f"⚠️ S4 ERROR\n{e}"
                )

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

                logger.error(
                    f"Tracker error: {e}"
                )

                discord.send_error(
                    f"⚠️ TRACKER ERROR\n{e}"
                )

            last_run_slot = current_slot
            logger.info("=== SCAN COMPLETE ===")
            print_next_scan()

        time.sleep(10)

    except KeyboardInterrupt:

        discord.send_status(
            "🔴 ICT SCANNER BOT STOPPED"
        )
        logger.info("Bot stopped by user")
        print("\nBOT STOPPED BY USER\n")
        break

    except Exception as e:

        error_count += 1

        logger.error(
            f"Main loop error: {e}"
        )

        discord.send_error(
            f"🚨 ICT SCANNER ERROR\n\n{e}"
        )

        time.sleep(10)