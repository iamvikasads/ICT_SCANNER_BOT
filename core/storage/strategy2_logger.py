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

    # ==================================
    # INIT FILES
    # ==================================

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

                    "rank_score",

                    "liquidity_level",
                    "liquidity_type",
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

    # ==================================
    # SAVE SETUP
    # ==================================

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

                setup.get(
                    "rank_score",
                    0
                ),

                setup["liquidity_level"],

                setup["liquidity_type"],

                setup["status"]

            ])

    # ==================================
    # GET ACTIVE SETUP
    # ==================================

    def get_active_setup(
        self,
        symbol,
        direction
    ):

        if not os.path.exists(
            self.setup_file
        ):

            return None

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

                    return row

        return None

    # ==================================
    # DUPLICATE CHECK
    # ==================================

    def setup_exists(
        self,
        symbol,
        direction
    ):

        return (

            self.get_active_setup(
                symbol,
                direction
            )

            is not None

        )

    # ==================================
    # REPLACE SETUP
    # ==================================

    def replace_setup(
        self,
        old_setup_id,
        new_setup
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
                    old_setup_id
                ):

                    row["status"] = (
                        "REPLACED"
                    )

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

                    "rank_score",

                    "liquidity_level",
                    "liquidity_type",
                    "status"

                ]
            )

            writer.writeheader()

            writer.writerows(
                rows
            )

        self.save_setup(
            new_setup
        )

    # ==================================
    # SAVE ENTRY
    # ==================================

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

    # ==================================
    # READ WAITING SETUPS
    # ==================================

    def get_waiting_setups(
        self
    ):

        setups = []

        if not os.path.exists(
            self.setup_file
        ):

            return setups

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

    # ==================================
    # UPDATE STATUS
    # ==================================

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

                    "rank_score",

                    "liquidity_level",
                    "liquidity_type",
                    "status"

                ]
            )

            writer.writeheader()

            writer.writerows(
                rows
            )