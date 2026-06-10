from core.binance.downloader import OHLCVDownloader
from core.structure.swings import SwingDetector
from core.structure.mss import MSSDetector


def run_test():

    downloader = OHLCVDownloader()

    swing_detector = SwingDetector()

    mss_detector = MSSDetector()

    candles = downloader.get_ohlcv(
        symbol="BTCUSDT",
        interval="4h",
        limit=100
    )

    swings = swing_detector.detect_swings(candles)

    result = mss_detector.detect(
        candles,
        swings
    )

    print("\nMSS RESULT\n")

    print(result)


if __name__ == "__main__":
    run_test()