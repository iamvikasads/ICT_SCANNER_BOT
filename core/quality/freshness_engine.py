class FreshnessEngine:

    def __init__(self):
        pass

    # ==================================
    # ORDER BLOCK FRESHNESS
    # ==================================

    def is_ob_fresh(
        self,
        candles,
        ob
    ):

        if ob is None:
            return False

        ob_high = ob["ob_high"]
        ob_low = ob["ob_low"]

        origin_timestamp = (
            ob["timestamp"]
        )

        for candle in candles:

            if (
                candle["timestamp"]
                <= origin_timestamp
            ):
                continue

            direction = ob["direction"]

            if direction == "LONG":

                if candle["close"] < ob_low:
                    return False

            elif direction == "SHORT":

                if candle["close"] > ob_high:
                    return False

        return True

    # ==================================
    # FVG FRESHNESS
    # ==================================

    def is_fvg_fresh(
        self,
        candles,
        fvg
    ):

        if fvg is None:
            return False

        fvg_high = (
            fvg["fvg_high"]
        )

        fvg_low = (
            fvg["fvg_low"]
        )

        origin_timestamp = (
            fvg["timestamp"]
        )

        for candle in candles:

            if (
                candle["timestamp"]
                <= origin_timestamp
            ):
                continue

            touched = (

                candle["low"]
                <= fvg_high

                and

                candle["high"]
                >= fvg_low

            )

            if touched:
                return False

        return True