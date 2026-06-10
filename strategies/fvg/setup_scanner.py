class FVGSetupScanner:

    def __init__(self):
        pass

    def create_setup(
        self,
        symbol,
        mss_result,
        fvgs
    ):

        if not mss_result.get("mss"):

            return None

        direction = mss_result["mss"]

        window_start = mss_result["window_start"]

        window_end = mss_result["window_end"]

        matching_fvgs = []

        for fvg in fvgs:

            if not (
                window_start
                <= fvg["timestamp"]
                <= window_end
            ):
                continue

            if (
                direction == "bullish"
                and
                fvg["type"] == "bullish"
            ):

                matching_fvgs.append(
                    fvg
                )

            if (
                direction == "bearish"
                and
                fvg["type"] == "bearish"
            ):

                matching_fvgs.append(
                    fvg
                )

        if len(matching_fvgs) == 0:

            return None

        selected_fvg = matching_fvgs[-1]

        return {

            "symbol": symbol,

            "strategy": "MSS + FVG",

            "direction": (
                "LONG"
                if direction == "bullish"
                else "SHORT"
            ),

            "fvg_high": selected_fvg["fvg_high"],

            "fvg_low": selected_fvg["fvg_low"],

            "status": "WAITING"
        }