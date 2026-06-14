import time

from core.binance.client import BinanceClient
from core.binance.downloader import OHLCVDownloader
from core.structure.swings import SwingDetector
from core.structure.market_structure import MarketStructure
from core.structure.mss_v2 import MSSDetectorV2
from core.liquidity.liquidity_engine import LiquidityEngine
from services.stats_manager import StatsManager
from core.storage.strategy2_logger import Strategy2Logger

from strategies.extreme_ob.ob_detector_v2 import OrderBlockDetectorV2
from strategies.extreme_ob.setup_scanner_v4 import SetupScannerV4
from core.quality.freshness_engine import FreshnessEngine
from core.quality.ob_ranker import OBRanker
from core.quality.candidate_selector import CandidateSelector
from core.quality.setup_manager import SetupManager
from core.quality.pd_array_filter import PDArrayFilter


class Strategy2Scanner:

    def __init__(self, downloader=None):
        self.client = BinanceClient()
        self.downloader = downloader or OHLCVDownloader()
        self.swing_detector = SwingDetector()
        self.structure_detector = MarketStructure()
        self.mss_detector = MSSDetectorV2()
        self.logger = Strategy2Logger()
        self.liquidity_engine = LiquidityEngine()

        self.ob_detector = OrderBlockDetectorV2()
        self.freshness_engine = FreshnessEngine()
        self.ob_ranker = OBRanker()
        self.candidate_selector = CandidateSelector()
        self.setup_manager = SetupManager()
        self.pd_filter = PDArrayFilter()
        self.setup_scanner = SetupScannerV4()

    def scan_symbol(self, symbol):

        StatsManager.increment(
            "s2_symbols_scanned"
        )

        try:

            candles_4h = self.downloader.get_ohlcv(
                symbol=symbol,
                interval="4h",
                limit=200
            )

            swings = self.swing_detector.detect_swings(
                candles_4h,
                lookback=2
            )

            structure = self.structure_detector.analyze(
                swings
            )

            mss_result = self.mss_detector.detect(
                candles_4h,
                swings,
                structure["structure"]
            )

            if mss_result["mss"] is None:
                return

            StatsManager.increment(
                "s2_mss_found"
            )

            # OB Detection Pipeline
            candles_1h = self.downloader.get_ohlcv(
                symbol=symbol,
                interval="1h",
                limit=200
            )
            
            all_obs = self.ob_detector.detect(candles_1h, mss_result)
            
            # Check 1 — Guard against missing "obs"
            if not all_obs:
                return

            if not all_obs.get("obs"):
                return
            
            # Apply Filtered OBs
            filtered_obs = [
                ob
                for ob in all_obs["obs"]
                if ob.get("distance_to_mss", 999) <= 12
            ]

            filtered_obs = [
                ob
                for ob in filtered_obs
                if self.pd_filter.allow_ob(
                    ob,
                    mss_result
                )
            ]

            # Check 2 — Empty filtered list
            if not filtered_obs:
                return

            # Rank OBs
            ranked_obs = self.ob_ranker.score_all(
                filtered_obs,
                self.freshness_engine,
                candles_1h
            )
            
            # Check 3 — Empty ranked list
            if not ranked_obs:
                return
            
            # Select best OB
            best_ob = self.candidate_selector.select_best(
                ranked_obs
            )

            if best_ob is None:
                return

            StatsManager.increment(
                "s2_ob_found"
            )

            setup = self.setup_scanner.create_setup(
                symbol,
                mss_result,
                best_ob
            )

            if setup is None:
                return

            direction = setup["direction"]

            active_setup = self.logger.get_active_setup(
                symbol,
                direction
            )

            if not self.setup_manager.should_replace(
                active_setup,
                setup
            ):
                return

            liquidity = (
                self.liquidity_engine.find_liquidity(
                    direction=direction,
                    entry=(
                        (
                            setup["ob_high"]
                            +
                            setup["ob_low"]
                        ) / 2
                    ),
                    swings=swings
                )
            )

            if liquidity is None:
                return

            setup["setup_id"] = (
                f"{symbol}_"
                f"{mss_result['timestamp']}"
            )

            setup["timestamp"] = (
                mss_result["timestamp"]
            )

            setup["symbol"] = symbol

            setup["strategy"] = (
                "MSS + EXTREME OB V4"
            )

            setup["liquidity_level"] = (
                liquidity["level"]
            )

            setup["liquidity_type"] = (
                liquidity["type"]
            )

            setup["status"] = "WAITING"

            if active_setup is None:
                self.logger.save_setup(
                    setup
                )
            else:
                self.logger.replace_setup(
                    active_setup["setup_id"],
                    setup
                )

            StatsManager.increment(
                "s2_setups_saved"
            )

            print(
                f"[S2] SETUP SAVED -> "
                f"{symbol} "
                f"{direction} "
                f"{liquidity['type']} "
                f"{liquidity['level']}"
            )

        except Exception as e:

            print(
                f"[S2 ERROR] "
                f"{symbol}: {e}"
            )

    def run(self):

        symbols = (
            self.client
            .get_top_25_symbols()
        )

        print(
            "\nSTRATEGY 2 SCANNER\n"
        )

        for symbol in symbols:

            self.scan_symbol(
                symbol
            )

            time.sleep(0.2)