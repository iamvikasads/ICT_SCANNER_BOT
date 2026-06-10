from core.risk.risk_engine import RiskEngine


def run_test():

    engine = RiskEngine()

    print("\n====================")
    print("TURTLE SOUP")
    print("====================\n")

    result = engine.turtle_soup(
        direction="LONG",
        entry=100,
        sweep_level=95
    )

    print(result)

    print("\n====================")
    print("EXTREME OB")
    print("====================\n")

    result = engine.extreme_ob(
        direction="LONG",
        entry=100,
        ob_high=101,
        ob_low=95
    )

    print(result)

    print("\n====================")
    print("FVG")
    print("====================\n")

    result = engine.fvg(
        direction="LONG",
        entry=100,
        fvg_high=101,
        fvg_low=96
    )

    print(result)


if __name__ == "__main__":
    run_test()