class FVGSetupScannerV4:

    def __init__(self):
        pass

    # ==================================
    # CREATE SETUP
    # ==================================

    def create_setup(
        self,
        symbol,
        mss_result,
        best_fvg
    ):

        if (
            mss_result is None
            or
            best_fvg is None
        ):

            return None

        mss_direction = (
            mss_result.get(
                "mss"
            )
        )

        if mss_direction is None:
            return None

        direction = (

            "LONG"

            if mss_direction
            ==
            "bullish"

            else

            "SHORT"

        )

        setup = {

            "symbol":
                symbol,

            "strategy":
                "MSS + FVG V4",

            "direction":
                direction,

            "fvg_high":
                best_fvg["fvg_high"],

            "fvg_low":
                best_fvg["fvg_low"],

            "rank_score":
                best_fvg.get(
                    "rank_score",
                    0
                ),

            "freshness_score":
                best_fvg.get(
                    "freshness_score",
                    0
                ),

            "gap_size":
                best_fvg.get(
                    "gap_size",
                    0
                ),

            "displacement_ratio":
                best_fvg.get(
                    "displacement_ratio",
                    0
                ),

            "distance_to_mss":
                best_fvg.get(
                    "distance_to_mss",
                    0
                ),

            "status":
                "WAITING"
        }

        return setup