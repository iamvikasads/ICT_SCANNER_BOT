import time
from core.binance.downloader import (
    OHLCVDownloader
)
from core.structure.swings import (
    SwingDetector
)
from core.liquidity.liquidity_engine import (
    LiquidityEngine
)
from services.stats_manager import (
    StatsManager
)
from core.storage.strategy4_logger import (
    Strategy4Logger
)

class Strategy4LiquidityScanner:

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

        self.liquidity_engine = (
            LiquidityEngine()
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

            entry = float(
                setup["mss_close"]
            )

            candles_4h = (
                self.downloader
                .get_ohlcv(
                    symbol=symbol,
                    interval="4h",
                    limit=200
                )
            )

            swings = (
                self.swing_detector
                .detect_swings(
                    candles_4h,
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
                return

            self.logger.update_liquidity(

                setup_id=
                    setup["setup_id"],

                liquidity_level=
                    liquidity["level"],

                liquidity_type=
                    liquidity["type"]

            )

            StatsManager.increment(
                "s4_liquidity_found"
            )

            print(
                f"[S4 LIQUIDITY] "
                f"{symbol} "
                f"{direction} "
                f"{liquidity['type']} "
                f"{liquidity['level']}"
            )

        except Exception as e:

            print(
                f"[S4 LIQUIDITY ERROR] "
                f"{setup['symbol']}: {e}"
            )

    def run(self):

        setups = (
            self.logger
            .get_waiting_liquidity_setups()
        )

        if not setups:

            print(
                "\n[S4 LIQUIDITY] "
                "No Waiting Setups\n"
            )

            return

        print(
            f"\n[S4 LIQUIDITY] "
            f"Checking "
            f"{len(setups)} "
            f"Setups\n"
        )

        for setup in setups:

            self.process_setup(
                setup
            )

            time.sleep(0.2)