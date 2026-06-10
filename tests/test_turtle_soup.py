from core.binance.downloader import OHLCVDownloader
from strategies.turtle_soup.detector import TurtleSoupDetector


def run_test():

    downloader = OHLCVDownloader()

    detector = TurtleSoupDetector()

    candles = downloader.get_ohlcv(
        symbol="BTCUSDT",
        interval="1h",
        limit=5
    )

    current_candle = candles[-1]

    daily_levels = downloader.get_previous_daily_levels(
        "BTCUSDT"
    )

    result = detector.detect(
        current_candle=current_candle,
        pdh=daily_levels["pdh"],
        pdl=daily_levels["pdl"]
    )

    print("\nPREVIOUS DAILY LEVELS\n")

    print(daily_levels)

    print("\nCURRENT 1H CANDLE\n")

    print(current_candle)

    print("\nTURTLE SOUP RESULT\n")

    print(result)


if __name__ == "__main__":
    run_test()