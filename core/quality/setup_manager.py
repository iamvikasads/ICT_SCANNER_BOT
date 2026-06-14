class SetupManager:

    def __init__(self):
        pass

    # ==================================
    # SHOULD REPLACE
    # ==================================

    def should_replace(
        self,
        current_setup,
        new_setup
    ):

        if current_setup is None:
            return True

        try:

            current_score = int(
                float(
                    current_setup.get(
                        "rank_score",
                        0
                    )
                )
            )

        except Exception:

            current_score = 0

        try:

            new_score = int(
                float(
                    new_setup.get(
                        "rank_score",
                        0
                    )
                )
            )

        except Exception:

            new_score = 0

        return (
            new_score
            >
            current_score
        )

    # ==================================
    # SELECT ACTIVE
    # ==================================

    def select_active(
        self,
        current_setup,
        new_setup
    ):

        if self.should_replace(
            current_setup,
            new_setup
        ):

            return new_setup

        return current_setup

    # ==================================
    # GROUP KEY
    # ==================================

    def get_key(
        self,
        setup
    ):

        symbol = (
            setup.get(
                "symbol",
                ""
            )
        )

        direction = (
            setup.get(
                "direction",
                ""
            )
        )

        return (
            f"{symbol}_{direction}"
        )

    # ==================================
    # BEST SETUPS
    # ==================================

    def select_best_setups(
        self,
        setups
    ):

        active = {}

        for setup in setups:

            key = (
                self.get_key(
                    setup
                )
            )

            current = (
                active.get(key)
            )

            active[key] = (
                self.select_active(
                    current,
                    setup
                )
            )

        return list(
            active.values()
        )