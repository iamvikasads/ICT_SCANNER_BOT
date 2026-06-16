class ExternalSwingFilter:

    def __init__(self):
        pass

    def filter(
        self,
        swings
    ):

        filtered = []

        for swing in swings:

            if not filtered:
                filtered.append(swing)
                continue

            last = filtered[-1]

            if (
                last["type"]
                ==
                swing["type"]
            ):

                if (
                    swing["type"]
                    ==
                    "swing_low"
                ):

                    if (
                        swing["price"]
                        <
                        last["price"]
                    ):
                        filtered[-1] = swing

                else:

                    if (
                        swing["price"]
                        >
                        last["price"]
                    ):
                        filtered[-1] = swing

            else:

                filtered.append(
                    swing
                )

       
        return filtered