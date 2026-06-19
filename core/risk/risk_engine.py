class RiskEngine:

    RR = 2.5

    MIN_RISK_PCT = 0.003

    MIN_RR = 2.0
    MAX_RR = 3.0

    def __init__(self):
        pass

    def _is_valid_risk(
        self,
        entry,
        risk
    ):

        if entry <= 0:
            return False

        if risk <= 0:
            return False

        if (
            risk / entry
        ) < self.MIN_RISK_PCT:

            return False

        return True

    # ==================================
    # STRATEGY 1 OLD
    # ==================================

    def turtle_soup(
        self,
        direction,
        entry,
        sweep_level
    ):

        buffer = (
            sweep_level * 0.001
        )

        if direction == "LONG":

            sl = (
                sweep_level
                - buffer
            )

            risk = (
                entry - sl
            )

            tp = (
                entry
                + (risk * self.RR)
            )

        else:

            sl = (
                sweep_level
                + buffer
            )

            risk = (
                sl - entry
            )

            tp = (
                entry
                - (risk * self.RR)
            )

        if not self._is_valid_risk(
            entry,
            risk
        ):
            return None

        return {
            "entry": round(entry, 4),
            "sl": round(sl, 4),
            "tp": round(tp, 4),
            "rr": self.RR
        }

    # ==================================
    # STRATEGY 1 V3
    # TP = NEXT LIQUIDITY
    # ==================================

    def turtle_soup_v3(
        self,
        direction,
        entry,
        sweep_level,
        liquidity_level
    ):

        buffer = (
            sweep_level * 0.001
        )

        if direction == "LONG":

            sl = (
                sweep_level
                - buffer
            )

            risk = (
                entry - sl
            )

            reward = (
                liquidity_level
                - entry
            )

        else:

            sl = (
                sweep_level
                + buffer
            )

            risk = (
                sl - entry
            )

            reward = (
                entry
                - liquidity_level
            )

        if not self._is_valid_risk(
            entry,
            risk
        ):
            return None

        if reward <= 0:
            return None

        rr = (
            reward / risk
        )

        if rr < self.MIN_RR:
            return None

        if rr > self.MAX_RR:

            rr = self.MAX_RR

            if direction == "LONG":

                tp = (
                    entry
                    + (risk * rr)
                )

            else:

                tp = (
                    entry
                    - (risk * rr)
                )

        else:

            tp = liquidity_level

        return {

            "entry":
                round(entry, 4),

            "sl":
                round(sl, 4),

            "tp":
                round(tp, 4),

            "rr":
                round(rr, 2)
        }

    # ==================================
    # STRATEGY 2 V3
    # MSS + EXTREME OB
    # ==================================

    def extreme_ob(
        self,
        direction,
        entry,
        ob_high,
        ob_low,
        liquidity_level,
        latest_swing_low=None,
        latest_swing_high=None
    ):

        buffer = (
            abs(
                ob_high - ob_low
            ) * 0.10
        )

        if direction == "LONG":

            base_sl = ob_low

            if latest_swing_low is not None:
                base_sl = min(
                    ob_low,
                    latest_swing_low
                )

            sl = (
                base_sl - buffer
            )

            risk = (
                entry - sl
            )

            reward = (
                liquidity_level
                - entry
            )

        else:

            base_sl = ob_high

            if latest_swing_high is not None:
                base_sl = max(
                    ob_high,
                    latest_swing_high
                )

            sl = (
                base_sl + buffer
            )

            risk = (
                sl - entry
            )

            reward = (
                entry
                - liquidity_level
            )

        if not self._is_valid_risk(
            entry,
            risk
        ):
            return None

        if reward <= 0:
            return None

        rr = (
            reward / risk
        )

        if rr < self.MIN_RR:
            return None

        if rr > self.MAX_RR:

            rr = self.MAX_RR

            if direction == "LONG":

                tp = (
                    entry
                    + (risk * rr)
                )

            else:

                tp = (
                    entry
                    - (risk * rr)
                )

        else:

            tp = liquidity_level

        return {

            "entry":
                round(entry, 4),

            "sl":
                round(sl, 4),

            "tp":
                round(tp, 4),

            "rr":
                round(rr, 2)
        }

    # ==================================
    # STRATEGY 3 V3
    # MSS + FVG
    # ==================================

    def fvg(
        self,
        direction,
        entry,
        fvg_high,
        fvg_low,
        liquidity_level,
        latest_swing_low=None,
        latest_swing_high=None
    ):

        buffer = (
            abs(
                fvg_high - fvg_low
            ) * 0.10
        )

        if direction == "LONG":

            base_sl = fvg_low

            if latest_swing_low is not None:
                base_sl = min(
                    fvg_low,
                    latest_swing_low
                )

            sl = (
                base_sl - buffer
            )

            risk = (
                entry - sl
            )

            reward = (
                liquidity_level
                - entry
            )

        else:

            base_sl = fvg_high

            if latest_swing_high is not None:
                base_sl = max(
                    fvg_high,
                    latest_swing_high
                )

            sl = (
                base_sl + buffer
            )

            risk = (
                sl - entry
            )

            reward = (
                entry
                - liquidity_level
            )

        if not self._is_valid_risk(
            entry,
            risk
        ):
            return None

        if reward <= 0:
            return None

        rr = (
            reward / risk
        )

        if rr < self.MIN_RR:
            return None

        if rr > self.MAX_RR:

            rr = self.MAX_RR

            if direction == "LONG":

                tp = (
                    entry
                    + (risk * rr)
                )

            else:

                tp = (
                    entry
                    - (risk * rr)
                )

        else:

            tp = liquidity_level

        return {

            "entry":
                round(entry, 4),

            "sl":
                round(sl, 4),

            "tp":
                round(tp, 4),

            "rr":
                round(rr, 2)
        }