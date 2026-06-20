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


class Strategy4EntryScanner:

    def __init__(self):

        self.logger = (
            Strategy4Logger()
        )

        self.trade_logger = (
            TradeLogger()
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

            liquidity_level = float(
                setup["liquidity_level"]
            )

            if direction == "LONG":

                sl = float(
                    setup["sweep_low"]
                )

                risk = (
                    entry
                    -
                    sl
                )

                if risk <= 0:
                    return

                tp = (
                    liquidity_level
                )

                reward = (
                    tp
                    -
                    entry
                )

            else:

                sl = float(
                    setup["sweep_high"]
                )

                risk = (
                    sl
                    -
                    entry
                )

                if risk <= 0:
                    return

                tp = (
                    liquidity_level
                )

                reward = (
                    entry
                    -
                    tp
                )

            if reward <= 0:
                return

            rr = (
                reward
                /
                risk
            )

            # =====================
            # MIN RR FILTER
            # =====================

            if rr < 2:
                return

            # =====================
            # CAP RR TO 3
            # =====================

            if rr > 3:

                if direction == "LONG":

                    tp = (
                        entry
                        +
                        (
                            risk
                            * 3
                        )
                    )

                else:

                    tp = (
                        entry
                        -
                        (
                            risk
                            * 3
                        )
                    )

                rr = 3.0

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