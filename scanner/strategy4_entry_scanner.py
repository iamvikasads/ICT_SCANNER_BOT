import time

from core.storage.strategy4_logger import (
    Strategy4Logger
)

from core.storage.trade_logger import (
    TradeLogger
)

from services.stats_manager import (
    StatsManager
)

from core.risk.risk_engine import (
    RiskEngine
)

from alerts.discord_client import (
    DiscordClient
)

from alerts.message_builder import (
    MessageBuilder
)

from core.binance.downloader import (
    OHLCVDownloader
)

from core.indicators.atr import ATR

from core.filters.volatility_filter import (
    VolatilityFilter
)


class Strategy4EntryScanner:

    def __init__(self):

        self.logger = (
            Strategy4Logger()
        )

        self.trade_logger = (
            TradeLogger()
        )

        self.risk_engine = (
            RiskEngine()
        )

        self.downloader = (
            OHLCVDownloader()
        )

        self.discord = (
            DiscordClient()
        )

        self.message_builder = (
            MessageBuilder()
        )

        self.volatility_filter = (
            VolatilityFilter()
        )

    def process_setup(
        self,
        setup
    ):

        try:

            direction = (
                setup["direction"]
            )

            entry = float(
                setup["mss_close"]
            )

            mss_high = float(
                setup["mss_high"]
            )

            mss_low = float(
                setup["mss_low"]
            )

            equilibrium = (
                mss_high
                +
                mss_low
            ) / 2

            liquidity_level = float(
                setup["liquidity_level"]
            )

            if (
                direction == "LONG"
                and
                entry > equilibrium
            ):

                print(
                    f"{setup['symbol']} -> PREMIUM LONG"
                )

                return

            if (
                direction == "SHORT"
                and
                entry < equilibrium
            ):

                print(
                    f"{setup['symbol']} -> DISCOUNT SHORT"
                )

                return

            candles_1h = (
                self.downloader.get_ohlcv(
                    symbol=setup["symbol"],
                    interval="1h",
                    limit=200
                )
            )

            atr = ATR.calculate(
                candles_1h
            )

            if not self.volatility_filter.is_active_enough(
                candles_1h
            ):

                print(
                    f"{setup['symbol']} -> LOW VOLATILITY"
                )

                return

            risk_data = (
                self.risk_engine.strategy4(
                    direction=direction,
                    entry=entry,
                    sweep_high=float(
                        setup["sweep_high"]
                    ),
                    sweep_low=float(
                        setup["sweep_low"]
                    ),
                    liquidity_level=liquidity_level,
                    atr=atr
                )
            )

            if risk_data is None:
                return

            entry = risk_data["entry"]
            sl = risk_data["sl"]
            tp = risk_data["tp"]
            rr = risk_data["rr"]

            entry_data = {

                "setup_id":
                    setup["setup_id"],

                "timestamp":
                    setup["timestamp"],

                "symbol":
                    setup["symbol"],

                "strategy":
                    "LIQUIDITY SWEEP + MSS",

                "direction":
                    direction,

                "entry":
                    entry,

                "sl":
                    sl,

                "tp":
                    tp,

                "rr":
                    round(
                        rr,
                        2
                    )
            }

            self.logger.save_entry(
                entry_data
            )

            trade_saved = (
                self.trade_logger
                .save_trade(
                    entry_data
                )
            )

            if not trade_saved:
                return

            self.logger.update_status(

                setup_id=
                    setup["setup_id"],

                status=
                    "TRIGGERED"

            )

            StatsManager.increment(
                "s4_entries_triggered"
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
                f"[S4 ENTRY] "
                f"{setup['symbol']} "
                f"{direction} "
                f"RR="
                f"{round(rr, 2)}"
            )

        except Exception as e:

            print(
                f"[S4 ENTRY ERROR] "
                f"{setup['symbol']}: {e}"
            )

    def run(self):

        setups = (
            self.logger
            .get_waiting_entry_setups()
        )

        if not setups:

            print(
                "\n[S4 ENTRY] "
                "No Waiting Setups\n"
            )

            return

        print(
            f"\n[S4 ENTRY] "
            f"Checking "
            f"{len(setups)} "
            f"Setups\n"
        )

        for setup in setups:

            self.process_setup(
                setup
            )

            time.sleep(0.2)