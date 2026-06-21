import time

from core.binance.client import BinanceClient
from core.binance.downloader import OHLCVDownloader

from services.stats_manager import StatsManager

from core.storage.strategy4_logger import (
    Strategy4Logger
)

from alerts.discord_client import (
    DiscordClient
)

from alerts.message_builder import (
    MessageBuilder
)


class Strategy4Scanner:

    def __init__(self, downloader=None):

        self.client = BinanceClient()

        self.downloader = (
            downloader
            or
            OHLCVDownloader()
        )

        self.logger = (
            Strategy4Logger()
        )

        self.discord = (
            DiscordClient()
        )

        self.message_builder = (
            MessageBuilder()
        )

    def scan_symbol(
        self,
        symbol
    ):

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

            direction = None
            liquidity = None

            # ==========================
            # PDL SWEEP
            # ==========================

            if (
                current_candle["low"]
                < pdl
            ):

                direction = "LONG"
                liquidity = "PDL"

            # ==========================
            # PDH SWEEP
            # ==========================

            elif (
                current_candle["high"]
                > pdh
            ):

                direction = "SHORT"
                liquidity = "PDH"

            else:

                return

            if self.logger.setup_exists(
                symbol,
                direction
            ):

                return

            setup = {

                "setup_id":
                    f"S4_"
                    f"{symbol}_"
                    f"{current_candle['timestamp']}",

                "timestamp":
                    current_candle["timestamp"],

                "symbol":
                    symbol,

                "strategy":
                    "LIQUIDITY SWEEP + MSS",

                "direction":
                    direction,

                "liquidity":
                    liquidity,

                "sweep_high":
                    current_candle["high"],

                "sweep_low":
                    current_candle["low"],

                "mss_high":
                    "",

                "mss_low":
                    "",

                "mss_close":
                    "",

                "liquidity_level":
                    "",

                "liquidity_type":
                    "",

                "status":
                    "WAITING_MSS"
            }

            self.logger.save_setup(
                setup
            )

            message = (
                self.message_builder
                .build_s4_setup_message(
                    setup
                )
            )

            self.discord.send_setup(
                message
            )

            StatsManager.increment(
                "s4_sweeps_found"
            )

            print(
                f"[S4 SWEEP] "
                f"{symbol} "
                f"{direction} "
                f"{liquidity}"
            )

        except Exception as e:

            print(
                f"[S4 ERROR] "
                f"{symbol}: {e}"
            )

    def run(self):

        symbols = (
            self.client
            .get_top_25_symbols()
        )

        print(
            "\nSTRATEGY 4 SCANNER\n"
        )

        for symbol in symbols:

            self.scan_symbol(
                symbol
            )

            time.sleep(0.2)