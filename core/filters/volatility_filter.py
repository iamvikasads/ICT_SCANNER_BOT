from core.indicators.atr import ATR


class VolatilityFilter:

    ATR_PERIOD = 14
    LOOKBACK = 50

    MIN_RATIO = 0.70

    def is_active_enough(
        self,
        candles
    ):

        try:

            current_atr = (
                ATR.calculate(
                    candles
                )
            )

            if (
                current_atr is None
            ):
                return True

            atr_values = []

            for i in range(

                self.ATR_PERIOD + 1,

                min(
                    len(candles),
                    self.LOOKBACK
                )

            ):

                atr = ATR.calculate(
                    candles[:i]
                )

                if atr is not None:

                    atr_values.append(
                        atr
                    )

            if not atr_values:
                return True

            average_atr = (

                sum(
                    atr_values
                )

                /

                len(
                    atr_values
                )

            )

            return (

                current_atr

                >=

                (
                    average_atr
                    *
                    self.MIN_RATIO
                )

            )

        except Exception:

            return True