class SweepDetector:

    # Minimum body-to-range ratio (displacement filter)
    MIN_BODY_RATIO = 0.50

    def detect(self, current_candle, pdh, pdl):

        candle_open = current_candle["open"]
        candle_high = current_candle["high"]
        candle_low = current_candle["low"]
        candle_close = current_candle["close"]

        candle_range = candle_high - candle_low

        if candle_range == 0:
            return {"sweep": False}

        body = abs(candle_close - candle_open)
        body_ratio = body / candle_range

        # FIX: Add displacement filter — body must be >= 50% of range
        if body_ratio < self.MIN_BODY_RATIO:
            return {"sweep": False}

        # PDL SWEEP: wick below PDL but close reclaims above PDL (bullish)
        if (
            candle_low < pdl
            and candle_close > pdl
        ):
            return {
                "sweep": True,
                "direction": "LONG",
                "liquidity": "PDL"
            }

        # PDH SWEEP: wick above PDH but close reclaims below PDH (bearish)
        if (
            candle_high > pdh
            and candle_close < pdh
        ):
            return {
                "sweep": True,
                "direction": "SHORT",
                "liquidity": "PDH"
            }

        return {"sweep": False}
