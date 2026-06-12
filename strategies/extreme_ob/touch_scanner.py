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

        zone_size = (
            zone_high - zone_low
        )

        zone_mid = (
            zone_high + zone_low
        ) / 2

        # ==================================
        # CE ENTRY BAND
        #
        # LONG:
        # midpoint -> 60%
        #
        # SHORT:
        # 40% -> midpoint
        # ==================================

        long_band_high = (
            zone_mid
            + (zone_size * 0.10)
        )

        short_band_low = (
            zone_mid
            - (zone_size * 0.10)
        )

        # ==================================
        # LONG TOUCH
        # ==================================

        if direction == "LONG":

            touched = (
                candle_low <= long_band_high
                and
                candle_high >= zone_mid
            )

            if not touched:
                return None

        # ==================================
        # SHORT TOUCH
        # ==================================

        elif direction == "SHORT":

            touched = (
                candle_high >= short_band_low
                and
                candle_low <= zone_mid
            )

            if not touched:
                return None

        else:
            return None

        candle_range = (
            candle_high - candle_low
        )

        if candle_range == 0:
            return None

        body = abs(
            candle_close - candle_open
        )

        body_ratio = (
            body / candle_range
        )

        # ==================================
        # LONG CONFIRMATION
        # ==================================

        if direction == "LONG":

            if candle_close <= candle_open:
                return None

            if body_ratio < self.MIN_BODY_RATIO:
                return None

            if candle_close < zone_mid:
                return None

        # ==================================
        # SHORT CONFIRMATION
        # ==================================

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