from core.binance.downloader import OHLCVDownloader

from core.structure.swings import SwingDetector

from core.structure.market_structure import MarketStructure

from core.structure.mss_v2 import MSSDetectorV2

from strategies.extreme_ob.ob_detector import (
    OrderBlockDetector
)

from strategies.extreme_ob.setup_scanner import (
    SetupScanner
)


def run_test():

    downloader = OHLCVDownloader()

    swing_detector = SwingDetector()

    structure_detector = MarketStructure()

    mss_detector = MSSDetectorV2()

    ob_detector = OrderBlockDetector()

    setup_scanner = SetupScanner()

    symbol = "BTCUSDT"

    # ======================
    # 4H DATA
    # ======================

    candles_4h = downloader.get_ohlcv(
        symbol=symbol,
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

    # ======================
    # 1H DATA
    # ======================

    candles_1h = downloader.get_ohlcv(
        symbol=symbol,
        interval="1h",
        limit=200
    )

    ob_result = ob_detector.detect(
        candles_1h=candles_1h,
        mss_result=mss_result
    )

    setup = setup_scanner.create_setup(
        symbol=symbol,
        mss_result=mss_result,
        ob_result=ob_result
    )

    print("\n====================")
    print("STRUCTURE")
    print("====================\n")

    print(structure_result)

    print("\n====================")
    print("MSS")
    print("====================\n")

    print(mss_result)

    print("\n====================")
    print("ORDER BLOCK")
    print("====================\n")

    print(ob_result)

    print("\n====================")
    print("SETUP")
    print("====================\n")

    print(setup)


if __name__ == "__main__":
    run_test()