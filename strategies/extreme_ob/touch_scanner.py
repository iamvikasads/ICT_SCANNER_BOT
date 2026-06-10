class TouchScanner:

    # Minimum body-to-range ratio for confirmation candle
    MIN_BODY_RATIO = 0.45

    def __init__(self):
        pass

    def check_touch(self, setup, candle_1h):

        if setup is None:
            return None

        zone_high = float(setup["ob_high"])
        zone_low = float(setup["ob_low"])
        direction = setup["direction"]

        candle_high = candle_1h["high"]
        candle_low = candle_1h["low"]
        candle_open = candle_1h["open"]
        candle_close = candle_1h["close"]

        # Basic touch: candle overlaps the OB zone
        touched = candle_low <= zone_high and candle_high >= zone_low

        if not touched:
            return None

        candle_range = candle_high - candle_low
        if candle_range == 0:
            return None

        body = abs(candle_close - candle_open)
        body_ratio = body / candle_range

        zone_mid = (zone_high + zone_low) / 2

        # LONG confirmation:
        # - Candle must close bullish
        # - Body must show displacement (>= 45% of range)
        # - Close must be above OB midpoint (strong reaction)
        if direction == "LONG":

            if candle_close <= candle_open:
                return None

            if body_ratio < self.MIN_BODY_RATIO:
                return None

            if candle_close < zone_mid:
                return None

        # SHORT confirmation:
        # - Candle must close bearish
        # - Body must show displacement
        # - Close must be below OB midpoint
        if direction == "SHORT":

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
