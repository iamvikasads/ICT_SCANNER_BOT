import time

from core.binance.client import BinanceClient
from core.binance.downloader import OHLCVDownloader

from strategies.turtle_soup.sweep_detector import SweepDetector

from core.storage.sweep_logger import SweepLogger
from core.storage.liquidity_state_manager import (
    LiquidityStateManager
)

from services.stats_manager import StatsManager

from alerts.discord_client import (
    DiscordClient
)

from alerts.message_builder import (
    MessageBuilder
)


class Strategy1Scanner:

    def __init__(self, downloader=None):

        self.client = BinanceClient()

        self.downloader = (
            downloader
            or
            OHLCVDownloader()
        )

        self.sweep_detector = (
            SweepDetector()
        )

        self.sweep_logger = (
            SweepLogger()
        )

        self.state_manager = (
            LiquidityStateManager()
        )

        self.discord = (
            DiscordClient()
        )

        self.message_builder = (
            MessageBuilder()
        )

    def _first_attempt_valid(
        self,
        candles,
        level,
        liquidity
    ):

        historical = candles[-24:-2]

        for candle in historical:

            if liquidity == "PDH":

                if candle["high"] >= level:

                    return False

            else:

                if candle["low"] <= level:

                    return False

        return True

    def scan_symbol(
        self,
        symbol
    ):

        StatsManager.increment(
            "s1_symbols_scanned"
        )

        try:

            daily_levels = (
                self.downloader
                .get_previous_day_levels(
                    symbol
                )
            )

            pdh = (
                daily_levels["pdh"]
            )

            pdl = (
                daily_levels["pdl"]
            )

            candles_1h = (
                self.downloader
                .get_ohlcv(
                    symbol=symbol,
                    interval="1h",
                    limit=100
                )
            )

            current_candle = (
                candles_1h[-2]
            )

            result = (
                self.sweep_detector
                .detect(
                    current_candle=current_candle,
                    pdh=pdh,
                    pdl=pdl
                )
            )

            if not result["sweep"]:
                return

            liquidity = (
                result["liquidity"]
            )

            direction = (
                result["direction"]
            )

            if (
                self.state_manager
                .is_consumed(
                    symbol,
                    liquidity
                )
            ):

                return

            level = (
                pdh
                if liquidity == "PDH"
                else pdl
            )

            first_attempt = (
                self._first_attempt_valid(
                    candles_1h,
                    level,
                    liquidity
                )
            )

            if not first_attempt:

                self.state_manager.mark_consumed(
                    symbol,
                    liquidity
                )

                return

            if (
                self.sweep_logger
                .sweep_exists(
                    current_candle["timestamp"],
                    symbol,
                    direction
                )
            ):

                return

            self.sweep_logger.save_sweep(
                timestamp=current_candle[
                    "timestamp"
                ],
                symbol=symbol,
                direction=direction,
                liquidity=liquidity,
                status="WAITING"
            )

            message = (
                self.message_builder
                .build_s1_setup_message(
                    symbol=symbol,
                    direction=direction,
                    liquidity=liquidity
                )
            )

            self.discord.send_setup(
                message
            )

            self.state_manager.mark_waiting(
                symbol,
                liquidity
            )

            StatsManager.increment(
                "s1_sweeps_found"
            )

            print(
                f"[SWEEP] "
                f"{symbol} "
                f"{direction} "
                f"{liquidity} "
                f"-> WAITING"
            )

        except Exception as e:

            print(
                f"[SWEEP ERROR] "
                f"{symbol}: {e}"
            )

    def run(self):

        symbols = (
            self.client
            .get_top_25_symbols()
        )

        print(
            "\nSTRATEGY 1 SWEEP SCANNER\n"
        )

        for symbol in symbols:

            self.scan_symbol(
                symbol
            )

            time.sleep(0.2)