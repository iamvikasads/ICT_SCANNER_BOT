from core.binance.downloader import OHLCVDownloader
from core.structure.swings import SwingDetector
from core.structure.market_structure import MarketStructure


class DailyBiasFilter:

    def __init__(self):
        self.downloader = OHLCVDownloader()
        self.swing_detector = SwingDetector()
        self.structure = MarketStructure()

    def get_bias(self, symbol):

        try:
            candles_1d = self.downloader.get_ohlcv(
                symbol=symbol,
                interval="1d",
                limit=60
            )

            confirmed = candles_1d[:-1]

            swings = self.swing_detector.detect_swings(
                confirmed,
                lookback=3
            )

            result = self.structure.analyze(swings)

            return result["structure"]

        except Exception as e:
            print(f"[BIAS ERROR] {symbol}: {e}")
            return "neutral"

    def allows_direction(self, symbol, direction):
        bias = self.get_bias(symbol)
        if direction == "LONG":
            return bias == "bullish"
        if direction == "SHORT":
            return bias == "bearish"
        return False
