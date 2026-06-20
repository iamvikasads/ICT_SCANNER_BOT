import time

from core.binance.downloader import OHLCVDownloader
from core.storage.strategy3_logger import Strategy3Logger
from core.storage.trade_logger import TradeLogger

from core.risk.risk_engine import RiskEngine

from strategies.fvg.touch_scanner import (
    FVGTouchScanner
)

from core.filters.daily_bias import (
    DailyBiasFilter
)

from alerts.discord_client import (
    DiscordClient
)

from alerts.message_builder import (
    MessageBuilder
)

from services.stats_manager import (
    StatsManager
)

from core.structure.swings import SwingDetector


class Strategy3EntryScanner:

    # 1. Change validity
    VALID_CANDLES = 192

    def __init__(
        self,
        downloader=None
    ):

        self.downloader = (
            downloader
            or
            OHLCVDownloader()
        )

        self.logger = (
            Strategy3Logger()
        )

        self.trade_logger = (
            TradeLogger()
        )

        self.risk_engine = (
            RiskEngine()
        )

        self.touch_scanner = (
            FVGTouchScanner()
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

        self.swing_detector = (
            SwingDetector()
        )

    def process_setup(
        self,
        setup
    ):

        try:

            symbol = (
                setup["symbol"]
            )

            direction = (
                setup["direction"]
            )

            setup_timestamp = int(
                setup["timestamp"]
            )

            fvg_high = float(
                setup["fvg_high"]
            )

            fvg_low = float(
                setup["fvg_low"]
            )

            liquidity_level = float(
                setup["liquidity_level"]
            )

            # 2. Replace candles_4h downloader block with candles_30m
            candles_30m = self.downloader.get_ohlcv(
                symbol=symbol,
                interval="30m",
                limit=100
            )

            if not candles_30m:
                return

            # 3. Replace loop over candles_4h with candles_30m
            candles_after = sum(

                1

                for c

                in candles_30m

                if (

                    c["timestamp"]
                    >
                    setup_timestamp

                )

            )

            if (

                candles_after

                >=

                self.VALID_CANDLES

            ):

                self.logger.update_status(

                    setup["setup_id"],

                    "EXPIRED"

                )

                StatsManager.increment(
                    "s3_expired"
                )

                print(
                    f"{symbol} "
                    f"-> Setup EXPIRED"
                )

                return

            # ======================
            # FVG INVALIDATION
            # ======================

            # 4. Replace loop variable candle in candles_4h with candles_30m
            for candle in candles_30m:

                if (

                    candle["timestamp"]

                    <=

                    setup_timestamp

                ):

                    continue

                if (

                    direction
                    ==
                    "LONG"

                    and

                    candle["close"]
                    <
                    fvg_low

                ):

                    self.logger.update_status(

                        setup["setup_id"],

                        "INVALIDATED"

                    )

                    StatsManager.increment(
                        "s3_invalidated"
                    )

                    print(
                        f"{symbol} "
                        f"-> FVG INVALIDATED"
                    )

                    return

                if (

                    direction
                    ==
                    "SHORT"

                    and

                    candle["close"]
                    >
                    fvg_high

                ):

                    self.logger.update_status(

                        setup["setup_id"],

                        "INVALIDATED"

                    )

                    StatsManager.increment(
                        "s3_invalidated"
                    )

                    print(
                        f"{symbol} "
                        f"-> FVG INVALIDATED"
                    )

                    return

            # 5. Replace candles_1h downloader block with candles_30m_entry
            candles_30m_entry = self.downloader.get_ohlcv(
                symbol=symbol,
                interval="30m",
                limit=50
            )

            # 6. Replace index checking and candle extraction for entry candles
            if len(candles_30m_entry) < 2:
                return

            candle = candles_30m_entry[-2]

            touch_result = (

                self.touch_scanner
                .check_touch(

                    setup,

                    candle

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
                self.risk_engine.fvg(
                    direction=direction,
                    entry=candle["close"],
                    fvg_high=fvg_high,
                    fvg_low=fvg_low,
                    liquidity_level=liquidity_level,
                    latest_swing_low=latest_swing_low,
                    latest_swing_high=latest_swing_high
                )
            )

            if risk is None:

                print(
                    f"{symbol} "
                    f"-> RR FILTERED"
                )

                return

            entry_data = {

                "setup_id":
                    setup["setup_id"],

                "timestamp":
                    candle["timestamp"],

                "symbol":
                    symbol,

                "strategy":
                    "MSS + FVG V4",

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
                "s3_entries_triggered"
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

                f"[S3 V4 ENTRY] "

                f"{symbol} "

                f"{direction} "

                f"RR={risk['rr']}"

            )

        except Exception as e:

            print(

                f"[S3 V4 ERROR] "

                f"{setup['symbol']}: "

                f"{e}"

            )

    def run(self):

        setups = (

            self.logger
            .get_waiting_setups()

        )

        if not setups:

            print(
                "\n[S3 V4] "
                "No Waiting Setups\n"
            )

            return

        print(

            f"\n[S3 V4] Checking "

            f"{len(setups)} "

            f"Waiting Setups\n"

        )

        for setup in setups:

            self.process_setup(
                setup
            )

            time.sleep(0.2)