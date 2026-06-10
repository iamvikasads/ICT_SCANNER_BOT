from strategies.fvg.touch_scanner import (
    FVGTouchScanner
)


def run_test():

    scanner = FVGTouchScanner()

    setup = {

        "symbol": "BTCUSDT",

        "strategy": "MSS + FVG",

        "direction": "LONG",

        "fvg_high": 105000,

        "fvg_low": 104500,

        "status": "WAITING"
    }

    candle_15m = {

        "timestamp": 123456789,

        "open": 105200,

        "high": 105250,

        "low": 104800,

        "close": 104950
    }

    result = scanner.check_touch(
        setup,
        candle_15m
    )

    print("\n====================")
    print("SETUP")
    print("====================\n")

    print(setup)

    print("\n====================")
    print("15M CANDLE")
    print("====================\n")

    print(candle_15m)

    print("\n====================")
    print("ENTRY RESULT")
    print("====================\n")

    print(result)


if __name__ == "__main__":
    run_test()