import time

from core.binance.client import BinanceClient
from core.binance.downloader import OHLCVDownloader

from core.structure.swings import SwingDetector
from core.structure.market_structure import MarketStructure
from core.structure.mss_v2 import MSSDetectorV2
from core.structure.external_swing_filter import (
    ExternalSwingFilter
)

from core.liquidity.liquidity_engine import LiquidityEngine

from services.stats_manager import StatsManager

from core.storage.strategy3_logger import Strategy3Logger

from strategies.fvg.fvg_detector_v2 import FVGDetectorV2
from strategies.fvg.setup_scanner_v4 import FVGSetupScannerV4

from core.quality.fvg_freshness_engine import (
    FVGFreshnessEngine
)

from core.quality.fvg_ranker import (
    FVGRanker
)

from core.quality.fvg_candidate_selector import (
    FVGCandidateSelector
)

from core.quality.fvg_setup_manager import (
    FVGSetupManager
)

from core.quality.pd_array_filter import (
    PDArrayFilter
)


class Strategy3Scanner:

    def __init__(
        self,
        downloader=None
    ):

        self.client = BinanceClient()

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
        
        self.external_filter = (
            ExternalSwingFilter()
        )

        self.fvg_detector = (
            FVGDetectorV2()
        )

        self.logger = (
            Strategy3Logger()
        )

        self.liquidity_engine = (
            LiquidityEngine()
        )

        self.freshness_engine = (
            FVGFreshnessEngine()
        )

        self.fvg_ranker = (
            FVGRanker()
        )

        self.selector = (
            FVGCandidateSelector()
        )

        self.setup_manager = (
            FVGSetupManager()
        )

        self.pd_filter = (
            PDArrayFilter()
        )

        self.setup_scanner = (
            FVGSetupScannerV4()
        )

    def scan_symbol(
        self,
        symbol
    ):

        StatsManager.increment(
            "s3_symbols_scanned"
        )

        try:

            # Keep core structure detection on 4H
            candles_4h = (
                self.downloader.get_ohlcv(
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
            
            structure_swings = (
                self.external_filter.filter(
                    swings
                )
            )

            structure = (
                self.structure_detector
                .analyze(
                    structure_swings
                )
            )

            mss_result = (
                self.mss_detector.detect(
                    candles_4h,
                    structure_swings,
                    structure["structure"]
                )
            )

            if (
                mss_result["mss"]
                is None
            ):
                return

            StatsManager.increment(
                "s3_mss_found"
            )

            # Fetch 1H candles for refined FVG detection
            candles_1h = (
                self.downloader.get_ohlcv(
                    symbol=symbol,
                    interval="1h",
                    limit=200
                )
            )

            # Safety check: Ensure 1H candles were returned
            if not candles_1h:
                return

            # Detect FVGs using 1H candles
            fvg_result = (
                self.fvg_detector.detect(
                    candles_1h,
                    mss_result
                )
            )

            if (
                not fvg_result
            ):
                return

            # Safety check: Explicitly verify fvgs key exists before ranking
            if not fvg_result.get(
                "fvgs"
            ):
                return

            filtered_fvgs = [

                fvg

                for fvg

                in fvg_result["fvgs"]

                if self.pd_filter.allow_fvg(
                    fvg,
                    mss_result
                )

            ]

            # Score FVGs using 1H candles
            ranked_fvgs = (
                self.fvg_ranker.score_all(
                    filtered_fvgs,
                    self.freshness_engine,
                    candles_1h
                )
            )

            ranked_fvgs = (
                self.selector
                .filter_fresh(
                    ranked_fvgs,
                    min_freshness=0.50
                )
            )

            if not ranked_fvgs:
                return

            best_fvg = (
                self.selector
                .select_best(
                    ranked_fvgs
                )
            )

            if best_fvg is None:
                return

            StatsManager.increment(
                "s3_fvg_found"
            )

            setup = (
                self.setup_scanner
                .create_setup(
                    symbol,
                    mss_result,
                    best_fvg
                )
            )

            if setup is None:
                return

            direction = (
                setup["direction"]
            )

            active_setup = (
                self.logger
                .get_active_setup(
                    symbol,
                    direction
                )
            )

            if not (
                self.setup_manager
                .should_replace(
                    active_setup,
                    setup
                )
            ):
                return

            # Keep liquidity engine tied to 4H swings
            liquidity = (

                self.liquidity_engine
                .find_liquidity(

                    direction=direction,

                    entry=(

                        (
                            setup["fvg_high"]
                            +
                            setup["fvg_low"]
                        )
                        / 2

                    ),

                    swings=swings
                )

            )

            if liquidity is None:
                return

            setup["setup_id"] = (

                f"{symbol}_"

                f"FVG_"

                f"{best_fvg['timestamp']}"

            )

            setup["timestamp"] = (
                best_fvg["timestamp"]
            )

            setup["symbol"] = symbol

            setup["liquidity_level"] = (
                liquidity["level"]
            )

            setup["liquidity_type"] = (
                liquidity["type"]
            )

            setup["status"] = (
                "WAITING"
            )

            if active_setup is None:

                self.logger.save_setup(
                    setup
                )

            else:

                self.logger.replace_setup(

                    active_setup[
                        "setup_id"
                    ],

                    setup

                )

            StatsManager.increment(
                "s3_setups_saved"
            )

            print(

                f"[S3 V4] "

                f"SETUP SAVED -> "

                f"{symbol} "

                f"{direction} "

                f"Score="

                f"{best_fvg['rank_score']}"

            )

        except Exception as e:

            print(
                f"[S3 ERROR] "
                f"{symbol}: {e}"
            )

    def run(self):

        symbols = (

            self.client
            .get_top_25_symbols()

        )

        print(
            "\nSTRATEGY 3 V4 SCANNER\n"
        )

        for symbol in symbols:

            self.scan_symbol(
                symbol
            )

            time.sleep(0.2)