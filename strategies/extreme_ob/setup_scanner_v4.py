class SetupScannerV4:

    def __init__(self):
        pass

    def create_setup(
        self,
        symbol,
        mss_result,
        ob
    ):

        if ob is None:
            return None

        direction = (
            ob["direction"]
        )

        setup = {

            "setup_id":

                f"{symbol}_"
                f"{mss_result['timestamp']}",

            "timestamp":

                mss_result[
                    "timestamp"
                ],

            "symbol":
                symbol,

            "strategy":
                "MSS + EXTREME OB V4",

            "direction":
                direction,

            "ob_high":
                ob["ob_high"],

            "ob_low":
                ob["ob_low"],

            "rank_score":
                ob.get(
                    "rank_score",
                    0
                ),

            "distance_to_mss":
                ob.get(
                    "distance_to_mss",
                    0
                ),

            "displacement_ratio":
                ob.get(
                    "displacement_ratio",
                    0
                ),

            "has_fvg":
                ob.get(
                    "has_fvg",
                    False
                ),

            "status":
                "WAITING"
        }

        return setup