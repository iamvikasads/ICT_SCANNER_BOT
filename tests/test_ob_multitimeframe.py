from core.binance.downloader import OHLCVDownloader

from core.structure.swings import SwingDetector

from core.structure.market_structure import MarketStructure

from core.structure.mss_v2 import MSSDetectorV2

from strategies.extreme_ob.ob_detector import (
    OrderBlockDetector
)


def run_test():

    downloader = OHLCVDownloader()

    swing_detector = SwingDetector()

    structure_detector = MarketStructure()

    mss_detector = MSSDetectorV2()

    ob_detector = OrderBlockDetector()

    # ==========================
    # 4H DATA
    # ==========================

    candles_4h = downloader.get_ohlcv(
        symbol="BTCUSDT",
        interval="4h",
        limit=100
    )

    swings = swing_detector.detect_swings(
        candles_4h
    )

    structure_result = structure_detector.analyze(
        swings
    )

    mss_result = mss_detector.detect(
        candles=candles_4h,
        swings=swings,
        structure=structure_result["structure"]
    )

    # ==========================
    # 1H DATA
    # ==========================

    candles_1h = downloader.get_ohlcv(
        symbol="BTCUSDT",
        interval="1h",
        limit=200
    )

    ob_result = ob_detector.detect(
    candles_1h=candles_1h,
    mss_result=mss_result
    )

    print("\n========================")
    print("4H STRUCTURE")
    print("========================\n")

    print(structure_result)

    print("\n========================")
    print("4H MSS")
    print("========================\n")

    print(mss_result)

    print("\n========================")
    print("1H ORDER BLOCK")
    print("========================\n")

    print(ob_result)


if __name__ == "__main__":
    run_test()