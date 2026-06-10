class RiskEngine:

    RR = 2.5
    MIN_RISK_PCT = 0.003  # 0.3% of entry minimum risk distance

    def __init__(self):
        pass

    def _is_valid_risk(self, entry, risk):
        if entry <= 0 or risk <= 0:
            return False
        if risk / entry < self.MIN_RISK_PCT:
            return False
        return True

    # ==================================
    # STRATEGY 1 — TURTLE SOUP
    # SL below/above the swept PDL/PDH
    # ==================================

    def turtle_soup(self, direction, entry, sweep_level):

        buffer = sweep_level * 0.001

        if direction == "LONG":
            sl = sweep_level - buffer
            risk = entry - sl
            tp = entry + (risk * self.RR)
        else:
            sl = sweep_level + buffer
            risk = sl - entry
            tp = entry - (risk * self.RR)

        if not self._is_valid_risk(entry, risk):
            return None

        return {
            "entry": round(entry, 4),
            "sl": round(sl, 4),
            "tp": round(tp, 4),
            "rr": self.RR
        }

    # ==================================
    # STRATEGY 2 — MSS + EXTREME OB
    # ==================================

    def extreme_ob(self, direction, entry, ob_high, ob_low):

        buffer = (ob_high - ob_low) * 0.1

        if direction == "LONG":
            sl = ob_low - buffer
            risk = entry - sl
            tp = entry + (risk * self.RR)
        else:
            sl = ob_high + buffer
            risk = sl - entry
            tp = entry - (risk * self.RR)

        if not self._is_valid_risk(entry, risk):
            return None

        return {
            "entry": round(entry, 4),
            "sl": round(sl, 4),
            "tp": round(tp, 4),
            "rr": self.RR
        }

    # ==================================
    # STRATEGY 3 — MSS + FVG
    # ==================================

    def fvg(self, direction, entry, fvg_high, fvg_low):

        buffer = (fvg_high - fvg_low) * 0.1

        if direction == "LONG":
            sl = fvg_low - buffer
            risk = entry - sl
            tp = entry + (risk * self.RR)
        else:
            sl = fvg_high + buffer
            risk = sl - entry
            tp = entry - (risk * self.RR)

        if not self._is_valid_risk(entry, risk):
            return None

        return {
            "entry": round(entry, 4),
            "sl": round(sl, 4),
            "tp": round(tp, 4),
            "rr": self.RR
        }
