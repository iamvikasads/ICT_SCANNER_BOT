import time

from core.binance.client import BinanceClient
from core.binance.downloader import OHLCVDownloader
from core.structure.swings import SwingDetector
from core.structure.market_structure import MarketStructure
from core.structure.mss_v2 import MSSDetectorV2
from strategies.fvg.fvg_detector import FVGDetector
from core.storage.strategy3_logger import Strategy3Logger


class Strategy3Scanner:

    def __init__(self, downloader=None):
        self.client = BinanceClient()
        self.downloader = downloader or OHLCVDownloader()
        self.swing_detector = SwingDetector()
        self.structure_detector = MarketStructure()
        self.mss_detector = MSSDetectorV2()
        self.fvg_detector = FVGDetector()
        self.logger = Strategy3Logger()

    def scan_symbol(self, symbol):

        try:

            candles_4h = self.downloader.get_ohlcv(
                symbol=symbol,
                interval="4h",
                limit=200
            )

            swings = self.swing_detector.detect_swings(candles_4h)
            structure = self.structure_detector.analyze(swings)
            print(
            f"{symbol} -> Structure: "
            f"{structure['structure']}"
            )
            mss_result = self.mss_detector.detect(
                candles_4h, swings, structure["structure"]
            )

            if mss_result["mss"] is None:
                print(f"{symbol} -> No MSS")
                return

            fvg_result = self.fvg_detector.detect(candles_4h, mss_result)

            if fvg_result["fvg"] is None:
                print(f"{symbol} -> No FVG")
                return

            direction = fvg_result["direction"]

            if self.logger.setup_exists(symbol, direction):
                print(f"{symbol} -> Setup Exists")
                return

            setup_data = {
                "setup_id": f"{symbol}_FVG_{fvg_result['timestamp']}",
                "timestamp": fvg_result["timestamp"],
                "symbol": symbol,
                "strategy": "MSS + FVG",
                "direction": direction,
                "fvg_high": fvg_result["fvg_high"],
                "fvg_low": fvg_result["fvg_low"],
                "status": "WAITING"
            }

            self.logger.save_setup(setup_data)
            print(f"[S3] SETUP SAVED -> {symbol} {direction}")

        except Exception as e:
            print(f"[S3 ERROR] {symbol}: {e}")

    def run(self):

        symbols = self.client.get_top_25_symbols()
        print("\nSTRATEGY 3 SCANNER\n")

        for symbol in symbols:
            self.scan_symbol(symbol)
            time.sleep(0.2)
