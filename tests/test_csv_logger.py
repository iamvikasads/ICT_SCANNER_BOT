from core.storage.csv_logger import CSVLogger


def run_test():

    logger = CSVLogger()

    setup = {

        "setup_id": "BTCUSDT_OB_001",

        "created_time": 123456,

        "symbol": "BTCUSDT",

        "strategy": "MSS + EXTREME OB",

        "direction": "LONG",

        "status": "WAITING",

        "zone_high": 105000,

        "zone_low": 104500
    }

    logger.log_setup(setup)

    entry = {

        "setup_id": "BTCUSDT_OB_001",

        "timestamp": 123999,

        "symbol": "BTCUSDT",

        "strategy": "MSS + EXTREME OB",

        "direction": "LONG",

        "entry": 104900,

        "sl": 104500,

        "tp": 105900,

        "rr": 2.5
    }

    logger.log_entry(entry)

    signal = {

        "timestamp": 123999,

        "symbol": "BTCUSDT",

        "strategy": "MSS + EXTREME OB",

        "signal_type": "ENTRY"
    }

    logger.log_signal(signal)

    print("\nCSV LOGGING TEST COMPLETED\n")


if __name__ == "__main__":
    run_test()