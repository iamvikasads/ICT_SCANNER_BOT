class SetupScanner:

    def __init__(self):
        pass

    def create_setup(
        self,
        symbol,
        mss_result,
        ob_result
    ):

        if not mss_result.get("mss"):

            return None

        if not ob_result.get("ob"):

            return None

        return {
            "symbol": symbol,
            "strategy": "MSS + EXTREME OB",
            "direction": ob_result["direction"],
            "ob_high": ob_result["ob_high"],
            "ob_low": ob_result["ob_low"],
            "status": "WAITING"
        }