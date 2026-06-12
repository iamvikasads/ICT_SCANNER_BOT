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

        high_break = (
            current_high > last_swing_high["price"] * 0.999
            or
            current_close > last_swing_high["price"]
        )

        low_break = (
            current_low < last_swing_low["price"] * 1.001
            or
            current_close < last_swing_low["price"]
        )

        

        # ==================================
        # BULLISH MSS (Reversal)
        # ==================================

        if (
            structure == "bearish"
            and high_break
            and bullish_close
            and displacement
        ):

            return {
                "mss": "bullish",
                "type": "mss",
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
        # BEARISH MSS (Reversal)
        # ==================================

        if (
            structure == "bullish"
            and low_break
            and bearish_close
            and displacement
        ):

            return {
                "mss": "bearish",
                "type": "mss",
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

        # ==================================
        # BULLISH BOS (Continuation)
        # ==================================

        if (
            structure == "bullish"
            and high_break
            and bullish_close
            and displacement
        ):

            return {
                "mss": "bullish",
                "type": "bos",
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
        # BEARISH BOS (Continuation)
        # ==================================

        if (
            structure == "bearish"
            and low_break
            and bearish_close
            and displacement
        ):

            return {
                "mss": "bearish",
                "type": "bos",
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