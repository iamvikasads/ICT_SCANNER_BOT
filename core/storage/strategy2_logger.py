import csv
import os


class Strategy2Logger:

    def __init__(self):

        self.setup_file = (
            "data/strategy2_setups.csv"
        )

        self.entry_file = (
            "data/strategy2_entries.csv"
        )

        self._initialize_files()

    def _initialize_files(self):

        if not os.path.exists(
            self.setup_file
        ):

            with open(
                self.setup_file,
                "w",
                newline=""
            ) as file:

                writer = csv.writer(
                    file
                )

                writer.writerow([
                    "setup_id",
                    "timestamp",
                    "symbol",
                    "strategy",
                    "direction",
                    "ob_high",
                    "ob_low",
                    "status"
                ])

        if not os.path.exists(
            self.entry_file
        ):

            with open(
                self.entry_file,
                "w",
                newline=""
            ) as file:

                writer = csv.writer(
                    file
                )

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

    # =====================
    # SAVE SETUP
    # =====================

    def save_setup(
        self,
        setup
    ):

        with open(
            self.setup_file,
            "a",
            newline=""
        ) as file:

            writer = csv.writer(
                file
            )

            writer.writerow([

                setup["setup_id"],

                setup["timestamp"],

                setup["symbol"],

                setup["strategy"],

                setup["direction"],

                setup["ob_high"],

                setup["ob_low"],

                setup["status"]
            ])

    # =====================
    # DUPLICATE CHECK
    # =====================

    def setup_exists(
        self,
        symbol,
        direction
    ):

        if not os.path.exists(
            self.setup_file
        ):

            return False

        with open(
            self.setup_file,
            "r"
        ) as file:

            reader = csv.DictReader(
                file
            )

            for row in reader:

                if (

                    row["symbol"]
                    ==
                    symbol

                    and

                    row["direction"]
                    ==
                    direction

                    and

                    row["status"]
                    ==
                    "WAITING"

                ):

                    return True

        return False

    # =====================
    # SAVE ENTRY
    # =====================

    def save_entry(
        self,
        entry
    ):

        with open(
            self.entry_file,
            "a",
            newline=""
        ) as file:

            writer = csv.writer(
                file
            )

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

    # =====================
    # READ SETUPS
    # =====================

    def get_waiting_setups(
        self
    ):

        setups = []

        with open(
            self.setup_file,
            "r"
        ) as file:

            reader = csv.DictReader(
                file
            )

            for row in reader:

                if (
                    row["status"]
                    ==
                    "WAITING"
                ):

                    setups.append(
                        row
                    )

        return setups

    # =====================
    # UPDATE STATUS
    # =====================

    def update_status(
        self,
        setup_id,
        status
    ):

        rows = []

        with open(
            self.setup_file,
            "r"
        ) as file:

            reader = csv.DictReader(
                file
            )

            for row in reader:

                if (
                    row["setup_id"]
                    ==
                    setup_id
                ):

                    row[
                        "status"
                    ] = status

                rows.append(
                    row
                )

        with open(
            self.setup_file,
            "w",
            newline=""
        ) as file:

            writer = csv.DictWriter(

                file,

                fieldnames=[

                    "setup_id",
                    "timestamp",
                    "symbol",
                    "strategy",
                    "direction",
                    "ob_high",
                    "ob_low",
                    "status"
                ]
            )

            writer.writeheader()

            writer.writerows(
                rows
            )