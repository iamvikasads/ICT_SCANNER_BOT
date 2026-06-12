class FVGDetector:

    def __init__(self):
        pass

    def detect(self, candles, mss_result):

        if not mss_result.get("mss"):
            return {"fvg": None}

        direction = mss_result["mss"]
        mss_timestamp = mss_result["timestamp"]

        # =====================
        # Find MSS candle index
        # =====================

        mss_index = None

        for i, candle in enumerate(candles):

            if candle["timestamp"] == mss_timestamp:
                mss_index = i
                break

        if mss_index is None:
            return {"fvg": None}

        # =====================
        # Search around MSS only
        # =====================

        search_candles = candles[
            max(0, mss_index - 3):
            min(len(candles), mss_index + 5)
        ]

        if len(search_candles) < 3:
            return {"fvg": None}

        best_fvg = None
        best_score = 0

        # =====================
        # BULLISH FVG
        # =====================

        if direction == "bullish":

            for i in range(len(search_candles) - 2):

                candle_1 = search_candles[i]
                candle_2 = search_candles[i + 1]
                candle_3 = search_candles[i + 2]

                body_1 = abs(
                    candle_1["close"]
                    - candle_1["open"]
                )

                body_2 = abs(
                    candle_2["close"]
                    - candle_2["open"]
                )

                if body_1 == 0:
                    continue

                # Strong displacement
                if body_2 < body_1 * 1.3:
                    continue

                # Displacement candle must be bullish
                if (
                    candle_2["close"]
                    <= candle_2["open"]
                ):
                    continue

                gap_size = (
                    candle_3["low"]
                    - candle_1["high"]
                )

                if gap_size <= 0:
                    continue

                # Minimum gap size
                min_gap = (
                    candle_2["close"]
                    * 0.0005
                )

                if gap_size < min_gap:
                    continue

                score = (
                    gap_size
                    * body_2
                )

                if score > best_score:

                    best_score = score

                    best_fvg = {
                        "fvg": "bullish",
                        "direction": "LONG",
                        "fvg_high": candle_3["low"],
                        "fvg_low": candle_1["high"],
                        "timestamp": candle_2["timestamp"]
                    }

        # =====================
        # BEARISH FVG
        # =====================

        if direction == "bearish":

            for i in range(len(search_candles) - 2):

                candle_1 = search_candles[i]
                candle_2 = search_candles[i + 1]
                candle_3 = search_candles[i + 2]

                body_1 = abs(
                    candle_1["close"]
                    - candle_1["open"]
                )

                body_2 = abs(
                    candle_2["close"]
                    - candle_2["open"]
                )

                if body_1 == 0:
                    continue

                # Strong displacement
                if body_2 < body_1 * 1.5:
                    continue

                # Displacement candle must be bearish
                if (
                    candle_2["close"]
                    >= candle_2["open"]
                ):
                    continue

                gap_size = (
                    candle_1["low"]
                    - candle_3["high"]
                )

                if gap_size <= 0:
                    continue

                # Minimum gap size
                min_gap = (
                    candle_2["close"]
                    * 0.0005
                )

                if gap_size < min_gap:
                    continue

                score = (
                    gap_size
                    * body_2
                )

                if score > best_score:

                    best_score = score

                    best_fvg = {
                        "fvg": "bearish",
                        "direction": "SHORT",
                        "fvg_high": candle_1["low"],
                        "fvg_low": candle_3["high"],
                        "timestamp": candle_2["timestamp"]
                    }

        return best_fvg or {"fvg": None}