class MarketStructure:

    MIN_PRICE_DIFF_PCT = 0.002  # 0.3% minimum between swings

    def __init__(self):
        pass

    def analyze(self, swings):

        highs = sorted(
            [s for s in swings if s["type"] == "swing_high"],
            key=lambda x: x["timestamp"]
        )

        lows = sorted(
            [s for s in swings if s["type"] == "swing_low"],
            key=lambda x: x["timestamp"]
        )

        if len(highs) < 2 or len(lows) < 2:
            return {"structure": "neutral"}

        previous_high = highs[-2]["price"]
        current_high = highs[-1]["price"]

        previous_low = lows[-2]["price"]
        current_low = lows[-1]["price"]

        # Filter near-equal swings (consolidation noise)
        high_diff_pct = abs(current_high - previous_high) / previous_high
        low_diff_pct = abs(current_low - previous_low) / previous_low

        if (
            high_diff_pct < self.MIN_PRICE_DIFF_PCT
            or low_diff_pct < self.MIN_PRICE_DIFF_PCT
        ):
            return {
                "structure": "neutral",
                "previous_high": previous_high,
                "current_high": current_high,
                "previous_low": previous_low,
                "current_low": current_low
            }

        # Bullish: Higher High + Higher Low
        if current_high > previous_high and current_low > previous_low:
            return {
                "structure": "bullish",
                "previous_high": previous_high,
                "current_high": current_high,
                "previous_low": previous_low,
                "current_low": current_low
            }

        # Bearish: Lower High + Lower Low
        if current_high < previous_high and current_low < previous_low:
            return {
                "structure": "bearish",
                "previous_high": previous_high,
                "current_high": current_high,
                "previous_low": previous_low,
                "current_low": current_low
            }

        return {
            "structure": "neutral",
            "previous_high": previous_high,
            "current_high": current_high,
            "previous_low": previous_low,
            "current_low": current_low
        }
