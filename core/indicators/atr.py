class ATR:

    @staticmethod
    def calculate(
        candles,
        period=14
    ):

        if len(candles) < period + 1:
            return None

        true_ranges = []

        for i in range(1, len(candles)):

            high = candles[i]["high"]
            low = candles[i]["low"]

            previous_close = (
                candles[i - 1]["close"]
            )

            tr = max(

                high - low,

                abs(
                    high
                    - previous_close
                ),

                abs(
                    low
                    - previous_close
                )

            )

            true_ranges.append(tr)

        if len(true_ranges) < period:
            return None

        atr = (
            sum(
                true_ranges[-period:]
            )
            /
            period
        )

        return atr