import time

from core.binance.downloader import OHLCVDownloader
from core.storage.strategy2_logger import Strategy2Logger
from core.storage.trade_logger import TradeLogger
from strategies.extreme_ob.touch_scanner import TouchScanner
from core.risk.risk_engine import RiskEngine
from core.filters.daily_bias import DailyBiasFilter
from core.structure.swings import SwingDetector

from alerts.discord_client import DiscordClient
from alerts.message_builder import MessageBuilder
from services.stats_manager import StatsManager


class Strategy2EntryScanner:

    VALID_CANDLES = 48

    def __init__(self, downloader=None):
        self.downloader = downloader or OHLCVDownloader()
        self.logger = Strategy2Logger()
        self.trade_logger = TradeLogger()
        self.touch_scanner = TouchScanner()
        self.risk_engine = RiskEngine()
        self.bias_filter = DailyBiasFilter()
        self.swing_detector = SwingDetector()

        self.discord = DiscordClient()
        self.message_builder = MessageBuilder()

    def process_setup(self, setup):

        try:

            symbol = setup["symbol"]

            direction = setup["direction"]

            setup_timestamp = int(
                setup["timestamp"]
            )

            ob_high = float(
                setup["ob_high"]
            )

            ob_low = float(
                setup["ob_low"]
            )

            liquidity_level = float(
                setup["liquidity_level"]
            )

            candles_30m = (
                self.downloader.get_ohlcv(
                    symbol=symbol,
                    interval="30m",
                    limit=100
                )
            )

            candles_after = sum(
                1
                for c in candles_30m
                if c["timestamp"]
                > setup_timestamp
            )

            if candles_after >= self.VALID_CANDLES:

                self.logger.update_status(
                    setup["setup_id"],
                    "EXPIRED"
                )

                print(
                    f"{symbol} -> Setup EXPIRED"
                )

                return

            for candle in candles_30m:

                if (
                    candle["timestamp"]
                    <= setup_timestamp
                ):
                    continue

                if (
                    direction == "LONG"
                    and
                    candle["close"] < ob_low
                ):

                    self.logger.update_status(
                        setup["setup_id"],
                        "INVALIDATED"
                    )

                    print(
                        f"{symbol} -> OB INVALIDATED"
                    )

                    return

                if (
                    direction == "SHORT"
                    and
                    candle["close"] > ob_high
                ):

                    self.logger.update_status(
                        setup["setup_id"],
                        "INVALIDATED"
                    )

                    print(
                        f"{symbol} -> OB INVALIDATED"
                    )

                    return

            candles_30m_entry = (
                self.downloader.get_ohlcv(
                    symbol=symbol,
                    interval="30m",
                    limit=50
                )
            )

            candle_30m = (
                candles_30m_entry[-2]
            )

            touch_result = (
                self.touch_scanner.check_touch(
                    setup,
                    candle_30m
                )
            )

            if touch_result is None:
                return

            candles_1h = self.downloader.get_ohlcv(
                symbol=symbol,
                interval="1h",
                limit=200
            )

            swings = self.swing_detector.detect_swings(
                candles_1h,
                lookback=3
            )

            latest_swing_low = None
            latest_swing_high = None

            swing_lows = [
                s for s in swings
                if s["type"] == "swing_low"
            ]

            swing_highs = [
                s for s in swings
                if s["type"] == "swing_high"
            ]

            if swing_lows:
                latest_swing_low = swing_lows[-1]["price"]

            if swing_highs:
                latest_swing_high = swing_highs[-1]["price"]

            risk = (
                self.risk_engine.extreme_ob(
                    direction=direction,
                    entry=candle_30m["close"],
                    ob_high=ob_high,
                    ob_low=ob_low,
                    liquidity_level=liquidity_level,
                    latest_swing_low=latest_swing_low,
                    latest_swing_high=latest_swing_high
                )
            )

            if risk is None:

                print(
                    f"{symbol} -> RR FILTERED"
                )

                return

            entry_data = {

                "setup_id":
                    setup["setup_id"],

                "timestamp":
                    candle_30m["timestamp"],

                "symbol":
                    symbol,

                "strategy":
                    setup["strategy"],

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

            self.logger.save_entry(
                entry_data
            )

            self.trade_logger.save_trade(
                entry_data
            )

            self.logger.update_status(
                setup["setup_id"],
                "TRIGGERED"
            )

            StatsManager.increment(
                "s2_entries_triggered"
            )

            message = (
                self.message_builder
                .build_entry_message(
                    entry_data
                )
            )

            self.discord.send_entry(
                message
            )

            print(
                f"[S2 ENTRY] "
                f"{symbol} "
                f"{direction} "
                f"RR={risk['rr']}"
            )

        except Exception as e:

            print(
                f"[S2 ENTRY ERROR] "
                f"{setup['symbol']}: {e}"
            )

    def run(self):

        setups = (
            self.logger
            .get_waiting_setups()
        )

        if not setups:

            print(
                "\n[S2] No Waiting Setups\n"
            )

            return

        print(
            f"\n[S2] Checking "
            f"{len(setups)} "
            f"Waiting Setups\n"
        )

        for setup in setups:

            self.process_setup(
                setup
            )

            time.sleep(0.2)