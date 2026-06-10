from core.binance.downloader import OHLCVDownloader


def run_test():

    downloader = OHLCVDownloader()

    candles = downloader.get_ohlcv(
        symbol="BTCUSDT",
        interval="1h",
        limit=5
    )

    print("\nBTCUSDT 1H CANDLES\n")

    for candle in candles:
        print(candle)


if __name__ == "__main__":
    run_test()