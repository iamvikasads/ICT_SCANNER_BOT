from core.binance.downloader import OHLCVDownloader

from core.structure.swings import SwingDetector

from core.structure.market_structure import MarketStructure

from core.structure.mss_v2 import MSSDetectorV2


def run_test():

    downloader = OHLCVDownloader()

    swing_detector = SwingDetector()

    structure_detector = MarketStructure()

    mss_detector = MSSDetectorV2()

    candles = downloader.get_ohlcv(
        symbol="BTCUSDT",
        interval="4h",
        limit=100
    )

    swings = swing_detector.detect_swings(
        candles
    )

    structure_result = structure_detector.analyze(
        swings
    )

    result = mss_detector.detect(
        candles=candles,
        swings=swings,
        structure=structure_result["structure"]
    )

    print("\n====================")
    print("STRUCTURE")
    print("====================\n")

    print(structure_result)

    print("\n====================")
    print("MSS V2 DEBUG")
    print("====================\n")

    print(result)

    if result.get("mss"):

        print("\nMSS CANDLE INDEX\n")

        print(
            result["mss_candle_index"]
        )


if __name__ == "__main__":
    run_test()