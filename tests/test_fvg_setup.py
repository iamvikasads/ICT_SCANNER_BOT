from core.binance.downloader import OHLCVDownloader

from core.structure.swings import SwingDetector

from core.structure.market_structure import MarketStructure

from core.structure.mss_v2 import MSSDetectorV2

from strategies.fvg.fvg_detector import (
    FVGDetector
)

from strategies.fvg.setup_scanner import (
    FVGSetupScanner
)


def run_test():

    downloader = OHLCVDownloader()

    swing_detector = SwingDetector()

    structure_detector = MarketStructure()

    mss_detector = MSSDetectorV2()

    fvg_detector = FVGDetector()

    setup_scanner = FVGSetupScanner()

    symbol = "BTCUSDT"

    # ====================
    # 4H MSS
    # ====================

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

    # ====================
    # 1H FVG
    # ====================

    candles_1h = downloader.get_ohlcv(
        symbol=symbol,
        interval="1h",
        limit=200
    )

    fvgs = fvg_detector.detect(
        candles_1h
    )

    setup = setup_scanner.create_setup(
        symbol=symbol,
        mss_result=mss_result,
        fvgs=fvgs
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
    print("FVG COUNT")
    print("====================\n")

    print(len(fvgs))

    print("\n====================")
    print("SETUP")
    print("====================\n")

    print(setup)


if __name__ == "__main__":
    run_test()