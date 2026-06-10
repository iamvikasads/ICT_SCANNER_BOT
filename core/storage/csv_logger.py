import csv
import os


class CSVLogger:

    def __init__(self):

        self.setup_file = "data/setups.csv"

        self.entry_file = "data/entries.csv"

        self.signal_file = "data/signals.csv"

        self._initialize_files()

    def _initialize_files(self):

        if not os.path.exists(self.setup_file):

            with open(
                self.setup_file,
                "w",
                newline=""
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "setup_id",
                    "created_time",
                    "symbol",
                    "strategy",
                    "direction",
                    "status",
                    "zone_high",
                    "zone_low"
                ])

        if not os.path.exists(self.entry_file):

            with open(
                self.entry_file,
                "w",
                newline=""
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "setup_id",
                    "timestamp",
                    "symbol",
                    "strategy",
                    "direction",
                    "entry",
                    "sl",
                    "tp",
                    "rr"
                ])

        if not os.path.exists(self.signal_file):

            with open(
                self.signal_file,
                "w",
                newline=""
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "timestamp",
                    "symbol",
                    "strategy",
                    "signal_type"
                ])

    # ==========================
    # SETUPS
    # ==========================

    def log_setup(self, setup):

        with open(
            self.setup_file,
            "a",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                setup["setup_id"],
                setup["created_time"],
                setup["symbol"],
                setup["strategy"],
                setup["direction"],
                setup["status"],
                setup["zone_high"],
                setup["zone_low"]
            ])

    # ==========================
    # ENTRIES
    # ==========================

    def log_entry(self, entry):

        with open(
            self.entry_file,
            "a",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                entry["setup_id"],
                entry["timestamp"],
                entry["symbol"],
                entry["strategy"],
                entry["direction"],
                entry["entry"],
                entry["sl"],
                entry["tp"],
                entry["rr"]
            ])

    # ==========================
    # SIGNALS
    # ==========================

    def log_signal(self, signal):

        with open(
            self.signal_file,
            "a",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                signal["timestamp"],
                signal["symbol"],
                signal["strategy"],
                signal["signal_type"]
            ])