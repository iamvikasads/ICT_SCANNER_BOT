import time

from core.binance.client import BinanceClient
from core.binance.downloader import OHLCVDownloader

from strategies.turtle_soup.detector import TurtleSoupDetector

from core.structure.swings import SwingDetector
from core.liquidity.liquidity_engine import LiquidityEngine

from core.storage.sweep_logger import SweepLogger
from core.storage.csv_logger import CSVLogger
from core.storage.trade_logger import TradeLogger

from core.risk.risk_engine import RiskEngine

from core.filters.daily_bias import DailyBiasFilter

from alerts.discord_client import DiscordClient
from alerts.message_builder import MessageBuilder
from services.stats_manager import StatsManager


class Strategy1EntryScanner:

    VALID_CANDLES = 10

    def __init__(self, downloader=None):

        self.client = BinanceClient()

        self.downloader = (
            downloader
            or
            OHLCVDownloader()
        )

        self.detector = (
            TurtleSoupDetector()
        )

        self.swing_detector = (
            SwingDetector()
        )

        self.liquidity_engine = (
            LiquidityEngine()
        )

        self.sweep_logger = (
            SweepLogger()
        )

        self.csv_logger = (
            CSVLogger()
        )

        self.trade_logger = (
            TradeLogger()
        )

        self.risk_engine = (
            RiskEngine()
        )

        self.bias_filter = (
            DailyBiasFilter()
        )

        self.discord = (
            DiscordClient()
        )

        self.message_builder = (
            MessageBuilder()
        )

    def process_sweep(
        self,
        sweep
    ):

        try:

            symbol = (
                sweep["symbol"]
            )

            sweep_timestamp = int(
                sweep["timestamp"]
            )

            direction = (
                sweep["direction"]
            )

            candles_30m = (
                self.downloader.get_ohlcv(
                    symbol=symbol,
                    interval="30m",
                    limit=100
                )
            )

            closed_after_sweep = sum(

                1

                for c in candles_30m

                if (
                    c["timestamp"]
                    >
                    sweep_timestamp
                )
            )

            if (
                closed_after_sweep
                >
                self.VALID_CANDLES
            ):

                self.sweep_logger.update_status(
                    sweep_timestamp,
                    symbol,
                    "EXPIRED"
                )

                StatsManager.increment(
                    "s1_expired"
                )

                print(
                    f"{symbol} -> EXPIRED"
                )

                return

            daily_levels = (
                self.downloader
                .get_previous_day_levels(
                    symbol
                )
            )

            current_30m = (
                candles_30m[-2]
            )

            # ==========================
            # WAITING INVALIDATION
            # ==========================

            if direction == "LONG":

                if (
                    current_30m["close"]
                    <
                    daily_levels["pdl"]
                ):

                    self.sweep_logger.update_status(
                        sweep_timestamp,
                        symbol,
                        "INVALIDATED"
                    )

                    StatsManager.increment(
                        "s1_invalidated"
                    )

                    print(
                        f"{symbol} "
                        f"-> INVALIDATED "
                        f"(Below PDL)"
                    )

                    return

            else:

                if (
                    current_30m["close"]
                    >
                    daily_levels["pdh"]
                ):

                    self.sweep_logger.update_status(
                        sweep_timestamp,
                        symbol,
                        "INVALIDATED"
                    )

                    StatsManager.increment(
                        "s1_invalidated"
                    )

                    print(
                        f"{symbol} "
                        f"-> INVALIDATED "
                        f"(Above PDH)"
                    )

                    return

            result = (
                self.detector.detect(
                    candles=candles_30m,
                    pdh=daily_levels["pdh"],
                    pdl=daily_levels["pdl"]
                )
            )

            if (
                result["signal"]
                is None
            ):

                print(
                    f"{symbol} -> WAITING"
                )

                return

            entry = (
                result["entry"]
            )

            sweep_level = (

                daily_levels["pdl"]

                if direction == "LONG"

                else

                daily_levels["pdh"]

            )

            swings = (
                self.swing_detector
                .detect_swings(
                    candles_30m,
                    lookback=2
                )
            )

            liquidity = (
                self.liquidity_engine
                .find_liquidity(
                    direction=direction,
                    entry=entry,
                    swings=swings
                )
            )

            if liquidity is None:

                print(
                    f"{symbol} -> "
                    f"No liquidity found"
                )

                return

            risk = (
                self.risk_engine
                .turtle_soup_v3(

                    direction=direction,

                    entry=entry,

                    sweep_level=sweep_level,

                    liquidity_level=(
                        liquidity["level"]
                    )
                )
            )

            if risk is None:

                print(
                    f"{symbol} -> "
                    f"RR FILTERED"
                )

                return

            entry_data = {

                "setup_id":

                    f"{symbol}_TS_"
                    f"{candles_30m[-2]['timestamp']}",

                "timestamp":

                    candles_30m[-2][
                        "timestamp"
                    ],

                "symbol":
                    symbol,

                "strategy":
                    "TURTLE SOUP V4",

                "direction":
                    direction,

                "entry":
                    risk["entry"],

                "sl":
                    risk["sl"],

                "tp":
                    risk["tp"],

                "rr":
                    risk["rr"]
            }

            self.csv_logger.log_entry(
                entry_data
            )

            self.trade_logger.save_trade(
                entry_data
            )

            self.csv_logger.log_signal({

                "timestamp":
                    candles_30m[-2][
                        "timestamp"
                    ],

                "symbol":
                    symbol,

                "strategy":
                    "TURTLE SOUP V4",

                "signal_type":
                    "ENTRY"
            })

            message = (
                self.message_builder
                .build_entry_message(
                    entry_data
                )
            )

            self.discord.send_entry(
                message
            )

            self.sweep_logger.update_status(
                sweep_timestamp,
                symbol,
                "TRIGGERED"
            )

            StatsManager.increment(
                "s1_entries_triggered"
            )

            print(
                f"[TS ENTRY] "
                f"{symbol} "
                f"{direction} "
                f"{liquidity['type']} "
                f"{liquidity['level']} "
                f"RR={risk['rr']}"
            )

        except Exception as e:

            print(
                f"[TS ENTRY ERROR] "
                f"{sweep['symbol']}: {e}"
            )

    def run(self):

        sweeps = (
            self.sweep_logger
            .get_waiting_sweeps()
        )

        if not sweeps:

            print(
                "\n[TS] No Waiting Sweeps\n"
            )

            return

        print(
            f"\n[TS] Checking "
            f"{len(sweeps)} "
            f"Waiting Sweeps\n"
        )

        for sweep in sweeps:

            self.process_sweep(
                sweep
            )

            time.sleep(0.2)