class FVGDetector:

    def __init__(self):
        pass

    def detect(self, candles, mss_result):

        if not mss_result.get("mss"):
            return {"fvg": None}

        direction = mss_result["mss"]
        mss_timestamp = mss_result["timestamp"]

        # Search candles AFTER the MSS for the FVG
        search_candles = [
            c for c in candles
            if c["timestamp"] >= mss_timestamp
        ]

        if len(search_candles) < 3:
            return {"fvg": None}

        # =====================
        # BULLISH FVG
        # Gap between candle_1 high and candle_3 low
        # =====================

        if direction == "bullish":

            for i in range(len(search_candles) - 2):

                candle_1 = search_candles[i]
                candle_2 = search_candles[i + 1]
                candle_3 = search_candles[i + 2]

                body_1 = abs(candle_1["close"] - candle_1["open"])
                body_2 = abs(candle_2["close"] - candle_2["open"])

                # Displacement: middle candle must be impulsive
                if body_1 == 0 or body_2 < body_1 * 1.2:
                    continue

                gap_size = candle_3["low"] - candle_1["high"]

                if gap_size > 0:
                    return {
                        "fvg": "bullish",
                        "direction": "LONG",
                        "fvg_high": candle_3["low"],
                        "fvg_low": candle_1["high"],
                        "timestamp": candle_2["timestamp"]
                    }

        # =====================
        # BEARISH FVG
        # Gap between candle_1 low and candle_3 high
        # =====================

        if direction == "bearish":

            for i in range(len(search_candles) - 2):

                candle_1 = search_candles[i]
                candle_2 = search_candles[i + 1]
                candle_3 = search_candles[i + 2]

                body_1 = abs(candle_1["close"] - candle_1["open"])
                body_2 = abs(candle_2["close"] - candle_2["open"])

                if body_1 == 0 or body_2 < body_1 * 1.2:
                    continue

                gap_size = candle_1["low"] - candle_3["high"]

                if gap_size > 0:
                    return {
                        "fvg": "bearish",
                        "direction": "SHORT",
                        "fvg_high": candle_1["low"],
                        "fvg_low": candle_3["high"],
                        "timestamp": candle_2["timestamp"]
                    }

        return {"fvg": None}
