class MessageBuilder:

    def __init__(self):
        pass

    def _direction_emoji(self, direction):
        return "📈" if direction == "LONG" else "📉"

    # ==================================
    # SETUP ALERT
    # ==================================

    def build_setup_message(self, setup):

        strategy = setup["strategy"]
        direction = setup["direction"]
        emoji = self._direction_emoji(direction)

        zone_label = ""
        zone_high = None
        zone_low = None

        if strategy == "MSS + EXTREME OB":
            zone_label = "OB Zone"
            zone_high = setup["ob_high"]
            zone_low = setup["ob_low"]

        elif strategy == "MSS + FVG":
            zone_label = "FVG Zone"
            zone_high = setup["fvg_high"]
            zone_low = setup["fvg_low"]

        else:
            return None

        return (
            f"{emoji} SETUP DETECTED\n"
            f"{'─' * 22}\n"
            f"Pair:      {setup['symbol']}\n"
            f"Strategy:  {strategy}\n"
            f"Direction: {direction}\n"
            f"{'─' * 22}\n"
            f"{zone_label}:\n"
            f"  H: {zone_high}\n"
            f"  L: {zone_low}\n"
            f"{'─' * 22}\n"
            f"Status: Waiting for touch"
        )

    # ==================================
    # ENTRY ALERT
    # ==================================

    def build_entry_message(self, entry):

        direction = entry["direction"]
        emoji = self._direction_emoji(direction)

        risk = float(entry["entry"]) - float(entry["sl"])
        if direction == "SHORT":
            risk = float(entry["sl"]) - float(entry["entry"])

        return (
            f"{emoji} ENTRY TRIGGERED\n"
            f"{'─' * 22}\n"
            f"Pair:      {entry['symbol']}\n"
            f"Strategy:  {entry['strategy']}\n"
            f"Direction: {direction}\n"
            f"{'─' * 22}\n"
            f"Entry:  {entry['entry']}\n"
            f"SL:     {entry['sl']}\n"
            f"TP:     {entry['tp']}\n"
            f"RR:     1 : {entry['rr']}\n"
            f"{'─' * 22}\n"
            f"Risk:   {abs(round(risk, 4))} pts"
        )

    # ==================================
    # SWEEP ALERT
    # ==================================

    def build_sweep_message(self, symbol, direction, liquidity):

        emoji = self._direction_emoji(direction)

        return (
            f"{emoji} LIQUIDITY SWEEP\n"
            f"{'─' * 22}\n"
            f"Pair:      {symbol}\n"
            f"Strategy:  Turtle Soup\n"
            f"Direction: {direction}\n"
            f"Swept:     {liquidity}\n"
            f"{'─' * 22}\n"
            f"Status: Waiting confirmation"
        )
