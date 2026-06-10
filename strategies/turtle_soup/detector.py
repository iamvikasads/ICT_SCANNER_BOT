class TurtleSoupDetector:

    def __init__(self):
        pass

    def detect(self, candles, pdh, pdl):

        if len(candles) < 20:
            return {"signal": None}

        # FIX: Use candles[-2] — confirmed closed 1H candle
        current = candles[-2]

        current_body = abs(current["close"] - current["open"])
        current_range = current["high"] - current["low"]

        if current_range == 0:
            return {"signal": None}

        displacement = current_body >= (current_range * 0.60)

        # Find latest swing high and swing low from confirmed candles
        # (exclude current and live candle)
        confirmed = candles[:-2]

        swing_high = None
        swing_low = None

        for i in range(len(confirmed) - 2, 2, -1):
            if (
                confirmed[i]["high"] > confirmed[i - 1]["high"]
                and confirmed[i]["high"] > confirmed[i + 1]["high"]
            ):
                swing_high = confirmed[i]["high"]
                break

        for i in range(len(confirmed) - 2, 2, -1):
            if (
                confirmed[i]["low"] < confirmed[i - 1]["low"]
                and confirmed[i]["low"] < confirmed[i + 1]["low"]
            ):
                swing_low = confirmed[i]["low"]
                break

        # Bullish Turtle Soup: PDL sweep + reclaim + MSS above swing high
        if (
            current["low"] < pdl
            and current["close"] > pdl
            and displacement
            and swing_high is not None
            and current["close"] > swing_high
        ):
            return {
                "signal": "long",
                "direction": "LONG",
                "entry": current["close"],
                "swing_high": swing_high,
                "swing_low": swing_low,
                "timestamp": current["timestamp"]
            }

        # Bearish Turtle Soup: PDH sweep + reclaim + MSS below swing low
        if (
            current["high"] > pdh
            and current["close"] < pdh
            and displacement
            and swing_low is not None
            and current["close"] < swing_low
        ):
            return {
                "signal": "short",
                "direction": "SHORT",
                "entry": current["close"],
                "swing_high": swing_high,
                "swing_low": swing_low,
                "timestamp": current["timestamp"]
            }

        return {"signal": None}
