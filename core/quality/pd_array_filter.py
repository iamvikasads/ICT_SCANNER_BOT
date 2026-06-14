class PDArrayFilter:

    def __init__(self):
        pass

    def get_equilibrium(
        self,
        mss_result
    ):

        swing_high = (
            mss_result[
                "mss_swing_high"
            ]["price"]
        )

        swing_low = (
            mss_result[
                "mss_swing_low"
            ]["price"]
        )

        equilibrium = (

            swing_high
            +
            swing_low

        ) / 2

        return {

            "high":
                swing_high,

            "low":
                swing_low,

            "eq":
                equilibrium
        }

    def allow_ob(
        self,
        ob,
        mss_result
    ):

        pd = self.get_equilibrium(
            mss_result
        )

        if pd is None:
            return False

        eq = pd["eq"]

        if ob["direction"] == "LONG":

            return (
                ob["ob_high"]
                <
                eq
            )

        if ob["direction"] == "SHORT":

            return (
                ob["ob_low"]
                >
                eq
            )

        return False

    def allow_fvg(
        self,
        fvg,
        mss_result
    ):

        pd = self.get_equilibrium(
            mss_result
        )

        if pd is None:
            return False

        eq = pd["eq"]

        if fvg["direction"] == "LONG":

            return (
                fvg["fvg_high"]
                <
                eq
            )

        if fvg["direction"] == "SHORT":

            return (
                fvg["fvg_low"]
                >
                eq
            )

        return False