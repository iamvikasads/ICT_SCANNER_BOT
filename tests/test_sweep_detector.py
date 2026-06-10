from strategies.turtle_soup.sweep_detector import (
    SweepDetector
)


def run_test():

    detector = SweepDetector()

    candle = {

        "high": 105,

        "low": 94,

        "close": 101
    }

    result = detector.detect(

        current_candle=candle,

        pdh=110,

        pdl=95
    )

    print(result)


if __name__ == "__main__":

    run_test()