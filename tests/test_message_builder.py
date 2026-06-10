from alerts.message_builder import (
    MessageBuilder
)


def run_test():

    builder = MessageBuilder()

    # ==========================
    # FVG SETUP
    # ==========================

    setup = {

        "symbol": "BTCUSDT",

        "strategy": "MSS + FVG",

        "direction": "LONG",

        "fvg_high": 104800,

        "fvg_low": 104500
    }

    print("\n====================")
    print("SETUP MESSAGE")
    print("====================\n")

    print(
        builder.build_setup_message(
            setup
        )
    )

    # ==========================
    # ENTRY MESSAGE
    # ==========================

    entry = {

        "symbol": "BTCUSDT",

        "strategy": "MSS + FVG",

        "direction": "LONG",

        "entry": 104650,

        "sl": 104200,

        "tp": 105775,

        "rr": 2.5
    }

    print("\n====================")
    print("ENTRY MESSAGE")
    print("====================\n")

    print(
        builder.build_entry_message(
            entry
        )
    )


if __name__ == "__main__":
    run_test()