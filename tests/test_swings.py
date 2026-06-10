from core.binance.downloader import OHLCVDownloader
from core.structure.swings import SwingDetector


def run_test():

    downloader = OHLCVDownloader()

    detector = SwingDetector()

    candles = downloader.get_ohlcv(
        symbol="BTCUSDT",
        interval="4h",
        limit=100
    )

    swings = detector.detect_swings(candles)

    print("\nDETECTED SWINGS\n")

    for swing in swings:

        print(
            f"{swing['type']} | "
            f"Price: {swing['price']} | "
            f"Index: {swing['index']}"
        )


if __name__ == "__main__":
    run_test()