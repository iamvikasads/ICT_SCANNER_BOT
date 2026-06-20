import csv
import os


class Strategy4Logger:

    def __init__(self):

        self.setup_file = (
            "data/strategy4_setups.csv"
        )

        self.entry_file = (
            "data/strategy4_entries.csv"
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
                    "liquidity",

                    "sweep_high",
                    "sweep_low",

                    "mss_high",
                    "mss_low",
                    "mss_close",

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

                setup["liquidity"],

                setup["sweep_high"],

                setup["sweep_low"],

                setup.get(
                    "mss_high",
                    ""
                ),

                setup.get(
                    "mss_low",
                    ""
                ),

                setup.get(
                    "mss_close",
                    ""
                ),

                setup.get(
                    "liquidity_level",
                    ""
                ),

                setup.get(
                    "liquidity_type",
                    ""
                ),

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
                    in [

                        "WAITING_MSS",
                        "WAITING_LIQUIDITY",
                        "WAITING_ENTRY"

                    ]

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
                    "liquidity",

                    "sweep_high",
                    "sweep_low",

                    "mss_high",
                    "mss_low",
                    "mss_close",

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
    # WAITING MSS SETUPS
    # ==================================

    def get_waiting_mss_setups(
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
                    "WAITING_MSS"
                ):

                    setups.append(
                        row
                    )

        return setups

    # ==================================
    # WAITING ENTRY SETUPS
    # ==================================

    def get_waiting_entry_setups(
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
                    "WAITING_ENTRY"
                ):

                    setups.append(
                        row
                    )

        return setups

    def get_waiting_liquidity_setups(
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
                    "WAITING_LIQUIDITY"
                ):

                    setups.append(
                        row
                    )

        return setups

    # ==================================
    # UPDATE MSS
    # ==================================

    def update_mss(
        self,
        setup_id,
        mss_high,
        mss_low,
        mss_close
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
                        "mss_high"
                    ] = str(
                        mss_high
                    )

                    row[
                        "mss_low"
                    ] = str(
                        mss_low
                    )

                    row[
                        "mss_close"
                    ] = str(
                        mss_close
                    )

                    row[
                        "status"
                    ] = (
                        "WAITING_LIQUIDITY"
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
                    "liquidity",

                    "sweep_high",
                    "sweep_low",

                    "mss_high",
                    "mss_low",
                    "mss_close",

                    "liquidity_level",
                    "liquidity_type",

                    "status"

                ]
            )

            writer.writeheader()

            writer.writerows(
                rows
            )

    # ==================================
    # UPDATE LIQUIDITY
    # ==================================

    def update_liquidity(
        self,
        setup_id,
        liquidity_level,
        liquidity_type
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
                        "liquidity_level"
                    ] = str(
                        liquidity_level
                    )

                    row[
                        "liquidity_type"
                    ] = (
                        liquidity_type
                    )

                    row[
                        "status"
                    ] = (
                        "WAITING_ENTRY"
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
                    "liquidity",

                    "sweep_high",
                    "sweep_low",

                    "mss_high",
                    "mss_low",
                    "mss_close",

                    "liquidity_level",
                    "liquidity_type",

                    "status"

                ]
            )

            writer.writeheader()

            writer.writerows(
                rows
            )

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
                    "liquidity",

                    "sweep_high",
                    "sweep_low",

                    "mss_high",
                    "mss_low",
                    "mss_close",

                    "liquidity_level",
                    "liquidity_type",

                    "status"

                ]
            )

            writer.writeheader()

            writer.writerows(
                rows
            )