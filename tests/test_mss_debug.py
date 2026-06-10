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

    print("\n==============================")
    print("SWING HIGHS")
    print("==============================\n")

    swing_highs = [
        swing
        for swing in swings
        if swing["type"] == "swing_high"
    ]

    for swing in swing_highs:

        print(
            f"Index: {swing['index']} | "
            f"Price: {swing['price']}"
        )

    print("\n==============================")
    print("SWING LOWS")
    print("==============================\n")

    swing_lows = [
        swing
        for swing in swings
        if swing["type"] == "swing_low"
    ]

    for swing in swing_lows:

        print(
            f"Index: {swing['index']} | "
            f"Price: {swing['price']}"
        )

    print("\n==============================")
    print("LATEST STRUCTURE LEVELS")
    print("==============================\n")

    if len(swing_highs) > 0:

        print(
            f"Last Swing High: "
            f"{swing_highs[-1]['price']}"
        )

    if len(swing_lows) > 0:

        print(
            f"Last Swing Low: "
            f"{swing_lows[-1]['price']}"
        )

    print(
        f"Current Close: "
        f"{candles[-1]['close']}"
    )

    print("\n==============================")
    print("MSS RESULT")
    print("==============================\n")

    result = mss_detector.detect(
        candles,
        swings
    )

    print(result)


if __name__ == "__main__":
    run_test()