class FVGDetectorV2:

    SEARCH_BEFORE_MSS = 8
    SEARCH_AFTER_MSS = 16

    def __init__(self):
        pass

    # ==================================
    # FIND MSS INDEX
    # ==================================

    def _find_mss_index(
        self,
        candles,
        mss_timestamp
    ):

        for i, candle in enumerate(
            candles
        ):

            if (
                candle["timestamp"]
                >= mss_timestamp
            ):

                return i

        return None

    # ==================================
    # BULLISH FVG
    # ==================================

    def _detect_bullish(
        self,
        search_candles,
        mss_index
    ):

        fvgs = []

        for i in range(
            len(search_candles) - 2
        ):

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

            displacement_ratio = (
                body_2 / body_1
            )

            if (
                displacement_ratio
                < 1.50
            ):
                continue

            if (
                candle_2["close"]
                <= candle_2["open"]
            ):
                continue

            gap_size = (

                candle_3["low"]

                -

                candle_1["high"]

            )

            if gap_size <= 0:
                continue

            min_gap = (
                candle_2["close"]
                * 0.0050
            )

            if gap_size < min_gap:
                continue

            fvgs.append({

                "type":
                    "bullish",

                "direction":
                    "LONG",

                "fvg_high":
                    candle_3["low"],

                "fvg_low":
                    candle_1["high"],

                "gap_size":
                    gap_size,

                "displacement_ratio":
                    round(
                        displacement_ratio,
                        2
                    ),

                "timestamp":
                    candle_2["timestamp"],

                "distance_to_mss":
                    abs(
                        mss_index
                        -
                        (i + 1)
                    )
            })

        return fvgs

    # ==================================
    # BEARISH FVG
    # ==================================

    def _detect_bearish(
        self,
        search_candles,
        mss_index
    ):

        fvgs = []

        for i in range(
            len(search_candles) - 2
        ):

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

            displacement_ratio = (
                body_2 / body_1
            )

            if (
                displacement_ratio
                < 1.50
            ):
                continue

            if (
                candle_2["close"]
                >= candle_2["open"]
            ):
                continue

            gap_size = (

                candle_1["low"]

                -

                candle_3["high"]

            )

            if gap_size <= 0:
                continue

            min_gap = (
                candle_2["close"]
                * 0.0050
            )

            if gap_size < min_gap:
                continue

            fvgs.append({

                "type":
                    "bearish",

                "direction":
                    "SHORT",

                "fvg_high":
                    candle_1["low"],

                "fvg_low":
                    candle_3["high"],

                "gap_size":
                    gap_size,

                "displacement_ratio":
                    round(
                        displacement_ratio,
                        2
                    ),

                "timestamp":
                    candle_2["timestamp"],

                "distance_to_mss":
                    abs(
                        mss_index
                        -
                        (i + 1)
                    )
            })

        return fvgs

    # ==================================
    # MAIN DETECTOR
    # ==================================

    def detect(
        self,
        candles,
        mss_result
    ):

        if (
            not mss_result
            or
            not mss_result.get(
                "mss"
            )
        ):

            return {
                "fvgs": []
            }

        mss_timestamp = (
            mss_result["timestamp"]
        )

        mss_direction = (
            mss_result["mss"]
        )

        mss_index = (
            self._find_mss_index(
                candles,
                mss_timestamp
            )
        )

        if mss_index is None:

            return {
                "fvgs": []
            }

        search_start = max(
            0,
            mss_index
            -
            self.SEARCH_BEFORE_MSS
        )

        search_end = min(
            len(candles),
            mss_index
            +
            self.SEARCH_AFTER_MSS
        )

        search_candles = candles[
            search_start:
            search_end
        ]

        local_mss_index = (
            mss_index
            -
            search_start
        )

        if (
            mss_direction
            ==
            "bullish"
        ):

            fvgs = (
                self._detect_bullish(
                    search_candles,
                    local_mss_index
                )
            )

        else:

            fvgs = (
                self._detect_bearish(
                    search_candles,
                    local_mss_index
                )
            )

        return {
            "fvgs": fvgs
        }