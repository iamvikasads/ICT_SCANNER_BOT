import time

from core.binance.downloader import (
    OHLCVDownloader
)

from core.structure.swings import (
    SwingDetector
)

from core.structure.market_structure import (
    MarketStructure
)

from core.structure.mss_v2 import (
    MSSDetectorV2
)

from services.stats_manager import (
    StatsManager
)

from core.storage.strategy4_logger import (
    Strategy4Logger
)


class Strategy4MSSScanner:

    def __init__(
        self,
        downloader=None
    ):

        self.downloader = (
            downloader
            or
            OHLCVDownloader()
        )

        self.swing_detector = (
            SwingDetector()
        )

        self.structure_detector = (
            MarketStructure()
        )

        self.mss_detector = (
            MSSDetectorV2()
        )

        self.logger = (
            Strategy4Logger()
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

            candles = (
                self.downloader
                .get_ohlcv(
                    symbol=symbol,
                    interval="30m",
                    limit=200
                )
            )

            swings = (
                self.swing_detector
                .detect_swings(
                    candles,
                    lookback=2
                )
            )

            structure = (
                self.structure_detector
                .analyze(
                    swings
                )
            )

            mss_result = (
                self.mss_detector
                .detect(
                    candles,
                    swings,
                    structure[
                        "structure"
                    ]
                )
            )

            if (
                mss_result["mss"]
                is None
            ):
                return

            # LONG setup requires bullish MSS

            if (
                direction
                ==
                "LONG"
                and
                mss_result["mss"]
                !=
                "bullish"
            ):
                return

            # SHORT setup requires bearish MSS

            if (
                direction
                ==
                "SHORT"
                and
                mss_result["mss"]
                !=
                "bearish"
            ):
                return

            mss_high = (
                mss_result[
                    "mss_swing_high"
                ]["price"]
            )

            mss_low = (
                mss_result[
                    "mss_swing_low"
                ]["price"]
            )

            mss_close = (
                candles[-2]["close"]
            )

            self.logger.update_mss(

                setup_id=
                    setup["setup_id"],

                mss_high=
                    mss_high,

                mss_low=
                    mss_low,

                mss_close=
                    mss_close

            )

            StatsManager.increment(
                "s4_mss_found"
            )

            print(
                f"[S4 MSS] "
                f"{symbol} "
                f"{direction}"
            )

        except Exception as e:

            print(
                f"[S4 MSS ERROR] "
                f"{setup['symbol']}: {e}"
            )

    def run(self):

        setups = (
            self.logger
            .get_waiting_mss_setups()
        )

        if not setups:

            print(
                "\n[S4 MSS] "
                "No Waiting Setups\n"
            )

            return

        print(
            f"\n[S4 MSS] "
            f"Checking "
            f"{len(setups)} "
            f"Setups\n"
        )

        for setup in setups:

            self.process_setup(
                setup
            )

            time.sleep(0.2)