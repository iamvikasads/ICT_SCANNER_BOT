from core.storage.sweep_logger import (
    SweepLogger
)


def run_test():

    logger = SweepLogger()

    timestamp = 123456789

    symbol = "BTCUSDT"

    print("\n====================")
    print("SAVE SWEEP")
    print("====================\n")

    logger.save_sweep(

        timestamp=timestamp,

        symbol=symbol,

        direction="LONG",

        liquidity="PDL"
    )

    print("\n====================")
    print("CSV CONTENT")
    print("====================\n")


    print("SWEEP SAVED")

    print("\n====================")
    print("CHECK EXISTS")
    print("====================\n")

    exists = logger.sweep_exists(

        timestamp=timestamp,

        symbol=symbol
    )

    print(exists)

    print("\n====================")
    print("UPDATE STATUS")
    print("====================\n")

    logger.update_status(

        timestamp=timestamp,

        symbol=symbol,

        new_status="CONFIRMED"
    )

    print("STATUS UPDATED")


if __name__ == "__main__":
    run_test()