import time
from core.binance.client import BinanceClient
from core.binance.downloader import OHLCVDownloader
from strategies.turtle_soup.sweep_detector import SweepDetector
from core.storage.sweep_logger import SweepLogger
from services.stats_manager import StatsManager

class Strategy1Scanner:

    def __init__(self, downloader=None):
        self.client = BinanceClient()

        # Accept shared downloader for API efficiency
        self.downloader = downloader or OHLCVDownloader()

        self.sweep_detector = SweepDetector()
        self.sweep_logger = SweepLogger()

    def scan_symbol(self, symbol):

        StatsManager.increment(
            "s1_symbols_scanned"
        )

        try:

            daily_levels = self.downloader.get_previous_day_levels(symbol)

            pdh = daily_levels["pdh"]
            pdl = daily_levels["pdl"]

            candles_1h = self.downloader.get_ohlcv(
                symbol=symbol,
                interval="1h",
                limit=100
            )

            # Use candles[-2]: confirmed closed candle
            current_candle = candles_1h[-2]

            result = self.sweep_detector.detect(
                current_candle=current_candle,
                pdh=pdh,
                pdl=pdl
            )

            if not result["sweep"]:
                return

            direction = result["direction"]

            # FIX: Duplicate check now includes direction
            if self.sweep_logger.sweep_exists(
                current_candle["timestamp"],
                symbol,
                direction
            ):
                
                return

            self.sweep_logger.save_sweep(
                timestamp=current_candle["timestamp"],
                symbol=symbol,
                direction=direction,
                liquidity=result["liquidity"],
                status="WAITING"
            )

            StatsManager.increment(
                "s1_sweeps_found"
            )

            print(
                f"[SWEEP] {symbol} {direction} "
                f"{result['liquidity']} -> WAITING"
            )

        except Exception as e:
            print(f"[SWEEP ERROR] {symbol}: {e}")

    def run(self):

        symbols = self.client.get_top_25_symbols()

        print(
            "\nSTRATEGY 1 SWEEP SCANNER\n"
        )

        for symbol in symbols:

            self.scan_symbol(symbol)

            time.sleep(0.2)