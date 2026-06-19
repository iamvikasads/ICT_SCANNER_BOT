class OrderBlockDetectorV2:

    def __init__(self):
        pass

    def detect(
        self,
        candles,
        mss_result
    ):

        if not mss_result.get(
            "mss"
        ):

            return {
                "obs": []
            }

        direction = (
            mss_result["mss"]
        )

        # FIX #4 — Map 4H MSS timestamp to correct index inside 1H candles
        mss_timestamp = (
            mss_result["timestamp"]
        )

        mss_index = next(
            (
                i
                for i, candle
                in enumerate(candles)
                if (
                    candle["timestamp"]
                    >=
                    mss_timestamp
                )
            ),
            len(candles) - 2
        )

        search_start = max(
            0,
            mss_index - 18
        )

        search_candles = (
            candles[
                search_start:mss_index
            ]
        )

        if len(
            search_candles
        ) < 3:

            return {
                "obs": []
            }

        candidates = []

        # ==================================
        # BULLISH OB
        # ==================================

        if direction == "bullish":

            for i in range(
                len(search_candles) - 2
            ):

                origin = (
                    search_candles[i]
                )

                candle_2 = (
                    search_candles[i + 1]
                )

                candle_3 = (
                    search_candles[i + 2]
                )

                if (
                    origin["close"]
                    >= origin["open"]
                ):
                    continue

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
                    body_2
                    <
                    body_1 * 1.4
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

                if (
                    ob_size
                    < min_size
                ):
                    continue

                gap_size = (
                    candle_3["low"]
                    - origin["high"]
                )

                has_fvg = (
                    gap_size > 0
                )

                distance = (
                    mss_index
                    -
                    (
                        search_start + i
                    )
                )

                candidates.append({

                    "ob": "bullish",

                    "direction":
                        "LONG",

                    "ob_high":
                        origin["high"],

                    "ob_low":
                        origin["low"],

                    "timestamp":
                        origin["timestamp"],

                    "has_fvg":
                        has_fvg,

                    "distance_to_mss":
                        distance,

                    "displacement_ratio":
                        displacement_ratio
                })

        # ==================================
        # BEARISH OB
        # ==================================

        if direction == "bearish":

            for i in range(
                len(search_candles) - 2
            ):

                origin = (
                    search_candles[i]
                )

                candle_2 = (
                    search_candles[i + 1]
                )

                candle_3 = (
                    search_candles[i + 2]
                )

                if (
                    origin["close"]
                    <= origin["open"]
                ):
                    continue

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
                    body_2
                    <
                    body_1 * 1.4
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

                if (
                    ob_size
                    < min_size
                ):
                    continue

                gap_size = (
                    origin["low"]
                    - candle_3["high"]
                )

                has_fvg = (
                    gap_size > 0
                )

                distance = (
                    mss_index
                    -
                    (
                        search_start + i
                    )
                )

                candidates.append({

                    "ob": "bearish",

                    "direction":
                        "SHORT",

                    "ob_high":
                        origin["high"],

                    "ob_low":
                        origin["low"],

                    "timestamp":
                        origin["timestamp"],

                    "has_fvg":
                        has_fvg,

                    "distance_to_mss":
                        distance,

                    "displacement_ratio":
                        displacement_ratio
                })

        return {
            "obs": candidates
        }