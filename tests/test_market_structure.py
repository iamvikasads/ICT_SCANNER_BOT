from core.binance.downloader import OHLCVDownloader
from core.structure.swings import SwingDetector
from core.structure.market_structure import MarketStructure


def run_test():

    downloader = OHLCVDownloader()

    swing_detector = SwingDetector()

    structure_detector = MarketStructure()

    candles = downloader.get_ohlcv(
        symbol="BTCUSDT",
        interval="4h",
        limit=100
    )

    swings = swing_detector.detect_swings(candles)

    result = structure_detector.analyze(swings)

    print("\nMARKET STRUCTURE\n")

    print(result)


if __name__ == "__main__":
    run_test()