class MSSDetectorV2:

    def __init__(self):
        pass

    def detect(self, candles, swings, structure):

        if len(candles) < 4:
            return {"mss": None}

        confirmed_candle = candles[-2]
        previous_candle = candles[-3]

        current_open = confirmed_candle["open"]
        current_close = confirmed_candle["close"]
        current_high = confirmed_candle["high"]
        current_low = confirmed_candle["low"]

        previous_open = previous_candle["open"]
        previous_close = previous_candle["close"]

        current_body = abs(
            current_close - current_open
        )

        previous_body = abs(
            previous_close - previous_open
        )

        displacement = (
            current_body > previous_body * 0.5
        )

        swing_highs = [
            s for s in swings
            if s["type"] == "swing_high"
        ]

        swing_lows = [
            s for s in swings
            if s["type"] == "swing_low"
        ]

        if not swing_highs or not swing_lows:
            return {"mss": None}

        last_swing_high = swing_highs[-1]
        last_swing_low = swing_lows[-1]

        confirmed_index = len(candles) - 2

        window_end = confirmed_candle["timestamp"]
        window_start = (
            window_end
            - (4 * 60 * 60 * 1000)
        )

        bullish_close = (
            current_close > current_open
        )

        bearish_close = (
            current_close < current_open
        )
        print(
        f"STRUCTURE={structure} | "
        f"HIGH_BREAK={current_high > last_swing_high['price']} | "
        f"LOW_BREAK={current_low < last_swing_low['price']} | "
        f"BULLISH_CLOSE={bullish_close} | "
        f"BEARISH_CLOSE={bearish_close} | "
        f"DISPLACEMENT={displacement}"
        )
        # ==================================
        # BULLISH MSS
        # ==================================

        if (
            structure == "bearish"
            and current_high >
            last_swing_high["price"]
            and bullish_close
            and displacement
        ):

            return {
                "mss": "bullish",
                "broken_level":
                    last_swing_high["price"],
                "broken_swing":
                    last_swing_high,
                "close":
                    current_close,
                "timestamp":
                    window_end,
                "window_start":
                    window_start,
                "window_end":
                    window_end,
                "mss_candle_index":
                    confirmed_index
            }

        # ==================================
        # BEARISH MSS
        # ==================================

        if (
            structure == "bullish"
            and current_low <
            last_swing_low["price"]
            and bearish_close
            and displacement
        ):

            return {
                "mss": "bearish",
                "broken_level":
                    last_swing_low["price"],
                "broken_swing":
                    last_swing_low,
                "close":
                    current_close,
                "timestamp":
                    window_end,
                "window_start":
                    window_start,
                "window_end":
                    window_end,
                "mss_candle_index":
                    confirmed_index
            }

        return {
            "mss": None
        }