import csv
import os


class Strategy3Logger:

    def __init__(self):
        self.setup_file = "data/strategy3_setups.csv"
        self.entry_file = "data/strategy3_entries.csv"
        self.ensure_files_exist()

    def ensure_files_exist(self):

        if not os.path.exists(self.setup_file):

            with open(
                self.setup_file,
                "w",
                newline="",
                encoding="utf-8"
            ) as f:

                csv.writer(f).writerow([

                    "setup_id",
                    "timestamp",
                    "symbol",
                    "strategy",
                    "direction",

                    "fvg_high",
                    "fvg_low",

                    "liquidity_level",
                    "liquidity_type",

                    "rank_score",
                    "freshness_score",

                    "status"
                ])

        if not os.path.exists(self.entry_file):

            with open(
                self.entry_file,
                "w",
                newline="",
                encoding="utf-8"
            ) as f:

                csv.writer(f).writerow([

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
    # ACTIVE SETUP
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
            "r",
            newline="",
            encoding="utf-8"
        ) as f:

            for row in csv.DictReader(f):

                if (

                    row["symbol"] == symbol

                    and

                    row["direction"] == direction

                    and

                    row["status"] == "WAITING"

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
    # SAVE SETUP
    # ==================================

    def save_setup(
        self,
        setup_data
    ):

        with open(
            self.setup_file,
            "a",
            newline="",
            encoding="utf-8"
        ) as f:

            csv.writer(f).writerow([

                setup_data["setup_id"],
                setup_data["timestamp"],
                setup_data["symbol"],
                setup_data["strategy"],
                setup_data["direction"],

                setup_data["fvg_high"],
                setup_data["fvg_low"],

                setup_data["liquidity_level"],
                setup_data["liquidity_type"],

                setup_data.get(
                    "rank_score",
                    0
                ),

                setup_data.get(
                    "freshness_score",
                    0
                ),

                setup_data["status"]
            ])

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
            "r",
            newline="",
            encoding="utf-8"
        ) as f:

            for row in csv.DictReader(f):

                if (
                    row["setup_id"]
                    ==
                    old_setup_id
                ):

                    row["status"] = (
                        "REPLACED"
                    )

                rows.append(row)

        with open(
            self.setup_file,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(

                f,

                fieldnames=[

                    "setup_id",
                    "timestamp",
                    "symbol",
                    "strategy",
                    "direction",

                    "fvg_high",
                    "fvg_low",

                    "liquidity_level",
                    "liquidity_type",

                    "rank_score",
                    "freshness_score",

                    "status"
                ]
            )

            writer.writeheader()

            writer.writerows(rows)

        self.save_setup(
            new_setup
        )

    # ==================================
    # GET WAITING
    # ==================================

    def get_waiting_setups(self):

        setups = []

        with open(
            self.setup_file,
            "r",
            newline="",
            encoding="utf-8"
        ) as f:

            for row in csv.DictReader(f):

                if (
                    row["status"]
                    ==
                    "WAITING"
                ):

                    setups.append(row)

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
            "r",
            newline="",
            encoding="utf-8"
        ) as f:

            for row in csv.DictReader(f):

                if (
                    row["setup_id"]
                    ==
                    setup_id
                ):

                    row["status"] = status

                rows.append(row)

        with open(
            self.setup_file,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(

                f,

                fieldnames=[

                    "setup_id",
                    "timestamp",
                    "symbol",
                    "strategy",
                    "direction",

                    "fvg_high",
                    "fvg_low",

                    "liquidity_level",
                    "liquidity_type",

                    "rank_score",
                    "freshness_score",

                    "status"
                ]
            )

            writer.writeheader()

            writer.writerows(rows)

    # ==================================
    # SAVE ENTRY
    # ==================================

    def save_entry(
        self,
        entry_data
    ):

        with open(
            self.entry_file,
            "a",
            newline="",
            encoding="utf-8"
        ) as f:

            csv.writer(f).writerow([

                entry_data["setup_id"],
                entry_data["timestamp"],
                entry_data["symbol"],
                entry_data["strategy"],
                entry_data["direction"],

                entry_data["entry"],
                entry_data["sl"],
                entry_data["tp"],
                entry_data["rr"]
            ])