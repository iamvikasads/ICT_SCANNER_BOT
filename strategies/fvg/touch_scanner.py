class FVGTouchScanner:

    # Minimum body-to-range ratio for confirmation
    MIN_BODY_RATIO = 0.45

    def __init__(self):
        pass

    def check_touch(self, setup, candle_1h):

        if setup is None:
            return None

        zone_high = float(setup["fvg_high"])
        zone_low = float(setup["fvg_low"])
        direction = setup["direction"]

        candle_high = candle_1h["high"]
        candle_low = candle_1h["low"]
        candle_open = candle_1h["open"]
        candle_close = candle_1h["close"]

        # Basic touch: candle overlaps the FVG zone
        touched = candle_low <= zone_high and candle_high >= zone_low

        if not touched:
            return None

        candle_range = candle_high - candle_low
        if candle_range == 0:
            return None

        body = abs(candle_close - candle_open)
        body_ratio = body / candle_range

        zone_mid = (zone_high + zone_low) / 2

        # LONG confirmation: bullish candle with displacement,
        # closing above FVG midpoint
        if direction == "LONG":

            if candle_close <= candle_open:
                return None

            if body_ratio < self.MIN_BODY_RATIO:
                return None

            if candle_close < zone_mid:
                return None

        # SHORT confirmation: bearish candle with displacement,
        # closing below FVG midpoint
        elif direction == "SHORT":

            if candle_close >= candle_open:
                return None

            if body_ratio < self.MIN_BODY_RATIO:
                return None

            if candle_close > zone_mid:
                return None

        return {
            "entry_triggered": True,
            "symbol": setup["symbol"],
            "strategy": setup["strategy"],
            "direction": direction,
            "entry": candle_close,
            "status": "TRIGGERED",
            "timestamp": candle_1h["timestamp"]
        }
