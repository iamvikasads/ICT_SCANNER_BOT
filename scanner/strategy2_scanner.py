import time

from core.binance.client import BinanceClient
from core.binance.downloader import OHLCVDownloader
from core.structure.swings import SwingDetector
from core.structure.market_structure import MarketStructure
from core.structure.mss_v2 import MSSDetectorV2
from strategies.extreme_ob.ob_detector import OrderBlockDetector
from strategies.extreme_ob.setup_scanner import SetupScanner
from core.storage.strategy2_logger import Strategy2Logger
from services.stats_manager import StatsManager


class Strategy2Scanner:

    def __init__(self, downloader=None):
        self.client = BinanceClient()
        self.downloader = downloader or OHLCVDownloader()
        self.swing_detector = SwingDetector()
        self.structure_detector = MarketStructure()
        self.mss_detector = MSSDetectorV2()
        self.ob_detector = OrderBlockDetector()
        self.setup_scanner = SetupScanner()
        self.logger = Strategy2Logger()

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

            ob_result = self.ob_detector.detect(
                candles_4h,
                mss_result
            )

            if ob_result["ob"] is None:
            
                return
            StatsManager.increment(
                "s2_ob_found"
            )

            setup = self.setup_scanner.create_setup(
                symbol,
                mss_result,
                ob_result
            )

            if setup is None:
                return

            direction = setup["direction"]

            if self.logger.setup_exists(
                symbol,
                direction
            ):
            
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
                "MSS + EXTREME OB"
            )

            setup["status"] = "WAITING"

            self.logger.save_setup(
                setup
            )
            StatsManager.increment(
             "s2_setups_saved"
            )

            print(
                f"[S2] SETUP SAVED -> "
                f"{symbol} {direction}"
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