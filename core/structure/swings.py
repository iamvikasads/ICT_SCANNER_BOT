class SwingDetector:

    def __init__(self):
        pass

    def detect_swings(self, candles, lookback=3):

        swings = []

        if len(candles) < (lookback * 2 + 1):
            return swings

        for i in range(lookback, len(candles) - lookback):

            current_high = candles[i]["high"]
            current_low = candles[i]["low"]

            # Swing High — all surrounding candles must be lower or equal
            is_swing_high = all(
                current_high >= candles[i - j]["high"]
                and current_high >= candles[i + j]["high"]
                for j in range(1, lookback + 1)
            )

            # Strict: at least one side must be strictly lower
            if is_swing_high and (
                current_high > candles[i - 1]["high"]
                or current_high > candles[i + 1]["high"]
            ):
                swings.append({
                    "type": "swing_high",
                    "index": i,
                    "timestamp": candles[i]["timestamp"],
                    "price": current_high
                })

            # Swing Low — all surrounding candles must be higher or equal
            is_swing_low = all(
                current_low <= candles[i - j]["low"]
                and current_low <= candles[i + j]["low"]
                for j in range(1, lookback + 1)
            )

            if is_swing_low and (
                current_low < candles[i - 1]["low"]
                or current_low < candles[i + 1]["low"]
            ):
                swings.append({
                    "type": "swing_low",
                    "index": i,
                    "timestamp": candles[i]["timestamp"],
                    "price": current_low
                })

        return swings
