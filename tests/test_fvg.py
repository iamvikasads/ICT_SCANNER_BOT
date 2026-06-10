from core.binance.downloader import OHLCVDownloader

from strategies.fvg.fvg_detector import (
    FVGDetector
)


def run_test():

    downloader = OHLCVDownloader()

    detector = FVGDetector()

    candles = downloader.get_ohlcv(
        symbol="BTCUSDT",
        interval="1h",
        limit=200
    )

    fvgs = detector.detect(
        candles
    )

    print("\n====================")
    print("FVG DETECTION")
    print("====================\n")

    print(
        f"Total FVGs Found: {len(fvgs)}"
    )

    print()

    for fvg in fvgs[-10:]:

        print(fvg)


if __name__ == "__main__":
    run_test()