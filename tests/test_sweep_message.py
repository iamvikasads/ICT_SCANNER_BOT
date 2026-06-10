from alerts.message_builder import (
    MessageBuilder
)


def run_test():

    builder = MessageBuilder()

    message = builder.build_sweep_message(

        symbol="BTCUSDT",

        direction="LONG",

        liquidity="PDL"
    )

    print(message)


if __name__ == "__main__":

    run_test()