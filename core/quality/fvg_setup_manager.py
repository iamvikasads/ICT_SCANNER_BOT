class FVGSetupManager:

    def __init__(self):
        pass

    # ==================================
    # SHOULD REPLACE
    # ==================================

    def should_replace(
        self,
        active_setup,
        new_setup
    ):

        # No active setup
        if active_setup is None:
            return True

        current_score = float(

            active_setup.get(
                "rank_score",
                0
            )

        )

        new_score = float(

            new_setup.get(
                "rank_score",
                0
            )

        )

        # Replace only if better
        if new_score > current_score:

            return True

        return False

    # ==================================
    # COMPARE SETUPS
    # ==================================

    def compare(
        self,
        active_setup,
        new_setup
    ):

        if active_setup is None:

            return {
                "replace": True,
                "reason": "NO_ACTIVE_SETUP"
            }

        current_score = float(

            active_setup.get(
                "rank_score",
                0
            )

        )

        new_score = float(

            new_setup.get(
                "rank_score",
                0
            )

        )

        if new_score > current_score:

            return {
                "replace": True,
                "reason": "HIGHER_SCORE"
            }

        return {
            "replace": False,
            "reason": "LOWER_SCORE"
        }