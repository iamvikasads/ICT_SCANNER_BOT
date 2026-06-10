from core.binance.client import BinanceClient


def run_test():

    client = BinanceClient()

    symbols = client.get_top_25_symbols()

    print("\nTOP 25 SYMBOLS\n")

    for symbol in symbols:
        print(symbol)


if __name__ == "__main__":
    run_test()