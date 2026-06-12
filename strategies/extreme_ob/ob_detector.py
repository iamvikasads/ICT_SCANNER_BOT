class OrderBlockDetector:

    def __init__(self):
        pass

    def detect(self, candles, mss_result):

        if not mss_result.get("mss"):
            return {"ob": None}

        direction = mss_result["mss"]
        mss_index = mss_result.get(
            "mss_candle_index",
            len(candles) - 2
        )

        search_start = max(
            0,
            mss_index - 15
        )

        search_candles = candles[
            search_start:mss_index
        ]

        if len(search_candles) < 3:
            return {"ob": None}

        candidates = []

        # =====================
        # BULLISH OB
        # =====================

        if direction == "bullish":

            for i in range(
                len(search_candles) - 2
            ):

                origin = search_candles[i]
                candle_2 = search_candles[i + 1]
                candle_3 = search_candles[i + 2]

                # Origin must be bearish
                if (
                    origin["close"]
                    >= origin["open"]
                ):
                    continue

                # Impulse candle must be bullish
                if (
                    candle_2["close"]
                    <= candle_2["open"]
                ):
                    continue

                body_1 = abs(
                    origin["close"]
                    - origin["open"]
                )

                body_2 = abs(
                    candle_2["close"]
                    - candle_2["open"]
                )

                if (
                    body_1 == 0
                    or
                    body_2 < body_1 * 1.4
                ):
                    continue

                displacement_ratio = (
                    body_2 / body_1
                )

                ob_size = (
                    origin["high"]
                    - origin["low"]
                )

                min_size = (
                    candle_2["close"]
                    * 0.0003
                )

                if ob_size < min_size:
                    continue

                gap_size = (
                    candle_3["low"]
                    - origin["high"]
                )

                has_fvg = (
                    gap_size > 0
                )

                score = 2

                if has_fvg:
                    score += 3

                distance = (
                    mss_index
                    - (search_start + i)
                )

                if distance <= 3:
                    score += 3
                elif distance <= 6:
                    score += 2
                elif distance <= 10:
                    score += 1

                final_score = (
                    score
                    * displacement_ratio
                )

                candidates.append({
                    "score": score,
                    "final_score": final_score,
                    "displacement_ratio":
                        displacement_ratio,
                    "ob": "bullish",
                    "direction": "LONG",
                    "ob_high":
                        origin["high"],
                    "ob_low":
                        origin["low"],
                    "timestamp":
                        origin["timestamp"],
                    "has_fvg":
                        has_fvg
                })

        # =====================
        # BEARISH OB
        # =====================

        if direction == "bearish":

            for i in range(
                len(search_candles) - 2
            ):

                origin = search_candles[i]
                candle_2 = search_candles[i + 1]
                candle_3 = search_candles[i + 2]

                # Origin must be bullish
                if (
                    origin["close"]
                    <= origin["open"]
                ):
                    continue

                # Impulse candle must be bearish
                if (
                    candle_2["close"]
                    >= candle_2["open"]
                ):
                    continue

                body_1 = abs(
                    origin["close"]
                    - origin["open"]
                )

                body_2 = abs(
                    candle_2["close"]
                    - candle_2["open"]
                )

                if (
                    body_1 == 0
                    or
                    body_2 < body_1 * 1.4
                ):
                    continue

                displacement_ratio = (
                    body_2 / body_1
                )

                ob_size = (
                    origin["high"]
                    - origin["low"]
                )

                min_size = (
                    candle_2["close"]
                    * 0.0003
                )

                if ob_size < min_size:
                    continue

                gap_size = (
                    origin["low"]
                    - candle_3["high"]
                )

                has_fvg = (
                    gap_size > 0
                )

                score = 2

                if has_fvg:
                    score += 3

                distance = (
                    mss_index
                    - (search_start + i)
                )

                if distance <= 3:
                    score += 3
                elif distance <= 6:
                    score += 2
                elif distance <= 10:
                    score += 1

                final_score = (
                    score
                    * displacement_ratio
                )

                candidates.append({
                    "score": score,
                    "final_score": final_score,
                    "displacement_ratio":
                        displacement_ratio,
                    "ob": "bearish",
                    "direction": "SHORT",
                    "ob_high":
                        origin["high"],
                    "ob_low":
                        origin["low"],
                    "timestamp":
                        origin["timestamp"],
                    "has_fvg":
                        has_fvg
                })

        if not candidates:
            return {"ob": None}

        best = max(
            candidates,
            key=lambda x: x["final_score"]
        )

        return best