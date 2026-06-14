class LiquidityEngine:

    EQ_TOLERANCE = 0.002

    def __init__(self):
        pass

    def _find_eqh(
        self,
        swing_highs,
        entry
    ):

        candidates = []

        for i in range(
            len(swing_highs) - 1
        ):

            h1 = swing_highs[i]
            h2 = swing_highs[i + 1]

            diff_pct = abs(
                h1["price"]
                -
                h2["price"]
            ) / h1["price"]

            if (
                diff_pct
                <=
                self.EQ_TOLERANCE
            ):

                level = max(
                    h1["price"],
                    h2["price"]
                )

                if level > entry:

                    candidates.append(
                        level
                    )

        if not candidates:
            return None

        return min(candidates)

    def _find_eql(
        self,
        swing_lows,
        entry
    ):

        candidates = []

        for i in range(
            len(swing_lows) - 1
        ):

            l1 = swing_lows[i]
            l2 = swing_lows[i + 1]

            diff_pct = abs(
                l1["price"]
                -
                l2["price"]
            ) / l1["price"]

            if (
                diff_pct
                <=
                self.EQ_TOLERANCE
            ):

                level = min(
                    l1["price"],
                    l2["price"]
                )

                if level < entry:

                    candidates.append(
                        level
                    )

        if not candidates:
            return None

        return max(candidates)

    def find_liquidity(
        self,
        direction,
        entry,
        swings
    ):

        swing_highs = [

            s

            for s in swings

            if (
                s["type"]
                ==
                "swing_high"
            )
        ]

        swing_lows = [

            s

            for s in swings

            if (
                s["type"]
                ==
                "swing_low"
            )
        ]

        # =====================
        # LONG
        # =====================

        if direction == "LONG":

            eqh = self._find_eqh(
                swing_highs,
                entry
            )

            if eqh:

                return {
                    "level": eqh,
                    "type": "EQH"
                }

            valid_highs = [

                s["price"]

                for s in swing_highs

                if (
                    s["price"]
                    >
                    entry
                )
            ]

            if valid_highs:

                return {

                    "level":
                        min(valid_highs),

                    "type":
                        "SWING_HIGH"
                }

            if swing_highs:

                return {

                    "level":
                        max(
                            s["price"]
                            for s
                            in swing_highs
                        ),

                    "type":
                        "EXTERNAL_LIQUIDITY"
                }

            return None

        # =====================
        # SHORT
        # =====================

        else:

            eql = self._find_eql(
                swing_lows,
                entry
            )

            if eql:

                return {
                    "level": eql,
                    "type": "EQL"
                }

            valid_lows = [

                s["price"]

                for s in swing_lows

                if (
                    s["price"]
                    <
                    entry
                )
            ]

            if valid_lows:

                return {

                    "level":
                        max(valid_lows),

                    "type":
                        "SWING_LOW"
                }

            if swing_lows:

                return {

                    "level":
                        min(
                            s["price"]
                            for s
                            in swing_lows
                        ),

                    "type":
                        "EXTERNAL_LIQUIDITY"
                }

            return None