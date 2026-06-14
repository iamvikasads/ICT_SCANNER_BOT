class FVGFreshnessEngine:

    MITIGATION_THRESHOLD = 0.50

    def __init__(self):
        pass

    # ==================================
    # BULLISH FVG
    # ==================================

    def _bullish_freshness(
        self,
        fvg,
        candles
    ):

        fvg_high = fvg["fvg_high"]
        fvg_low = fvg["fvg_low"]

        zone_size = (
            fvg_high - fvg_low
        )

        if zone_size <= 0:
            return 0

        timestamp = (
            fvg["timestamp"]
        )

        max_fill = 0

        for candle in candles:

            if (
                candle["timestamp"]
                <= timestamp
            ):
                continue

            if (
                candle["low"]
                >= fvg_high
            ):
                continue

            fill = (
                fvg_high
                -
                max(
                    candle["low"],
                    fvg_low
                )
            )

            fill_pct = (
                fill / zone_size
            )

            max_fill = max(
                max_fill,
                fill_pct
            )

        freshness = (
            1 - max_fill
        )

        return max(
            0,
            min(
                freshness,
                1
            )
        )

    # ==================================
    # BEARISH FVG
    # ==================================

    def _bearish_freshness(
        self,
        fvg,
        candles
    ):

        fvg_high = fvg["fvg_high"]
        fvg_low = fvg["fvg_low"]

        zone_size = (
            fvg_high - fvg_low
        )

        if zone_size <= 0:
            return 0

        timestamp = (
            fvg["timestamp"]
        )

        max_fill = 0

        for candle in candles:

            if (
                candle["timestamp"]
                <= timestamp
            ):
                continue

            if (
                candle["high"]
                <= fvg_low
            ):
                continue

            fill = (
                min(
                    candle["high"],
                    fvg_high
                )
                -
                fvg_low
            )

            fill_pct = (
                fill / zone_size
            )

            max_fill = max(
                max_fill,
                fill_pct
            )

        freshness = (
            1 - max_fill
        )

        return max(
            0,
            min(
                freshness,
                1
            )
        )

    # ==================================
    # SCORE
    # ==================================

    def score(
        self,
        fvg,
        candles
    ):

        direction = (
            fvg.get(
                "direction"
            )
        )

        if direction == "LONG":

            return self._bullish_freshness(
                fvg,
                candles
            )

        return self._bearish_freshness(
            fvg,
            candles
        )

    # ==================================
    # IS FRESH
    # ==================================

    def is_fresh(
        self,
        fvg,
        candles
    ):

        score = self.score(
            fvg,
            candles
        )

        return (
            score
            >=
            self.MITIGATION_THRESHOLD
        )