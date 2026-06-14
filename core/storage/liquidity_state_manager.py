import csv
import os
from datetime import datetime


class LiquidityStateManager:

    def __init__(self):

        self.file_path = (
            "data/liquidity_state.csv"
        )

        self.ensure_file_exists()

    def ensure_file_exists(self):

        if not os.path.exists(
            self.file_path
        ):

            os.makedirs(
                "data",
                exist_ok=True
            )

            with open(
                self.file_path,
                "w",
                newline="",
                encoding="utf-8"
            ) as f:

                csv.writer(f).writerow([

                    "date",

                    "symbol",

                    "liquidity",

                    "state"
                ])

    def _today(self):

        return datetime.utcnow().strftime(
            "%Y-%m-%d"
        )

    # ==================================
    # CHECK STATE
    # ==================================

    def get_state(
        self,
        symbol,
        liquidity
    ):

        self.ensure_file_exists()

        today = self._today()

        with open(
            self.file_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as f:

            reader = csv.DictReader(f)

            for row in reader:

                if (
                    row["date"] == today
                    and row["symbol"] == symbol
                    and row["liquidity"] == liquidity
                ):

                    return row["state"]

        return None

    # ==================================
    # SET STATE
    # ==================================

    def set_state(
        self,
        symbol,
        liquidity,
        state
    ):

        self.ensure_file_exists()

        today = self._today()

        rows = []

        updated = False

        with open(
            self.file_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as f:

            reader = csv.DictReader(f)

            for row in reader:

                if (
                    row["date"] == today
                    and row["symbol"] == symbol
                    and row["liquidity"] == liquidity
                ):

                    row["state"] = state

                    updated = True

                rows.append(row)

        if not updated:

            rows.append({

                "date":
                    today,

                "symbol":
                    symbol,

                "liquidity":
                    liquidity,

                "state":
                    state
            })

        with open(
            self.file_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(

                f,

                fieldnames=[

                    "date",

                    "symbol",

                    "liquidity",

                    "state"
                ]
            )

            writer.writeheader()

            writer.writerows(
                rows
            )

    # ==================================
    # HELPERS
    # ==================================

    def is_consumed(
        self,
        symbol,
        liquidity
    ):

        state = self.get_state(
            symbol,
            liquidity
        )

        return state in [

            "CONSUMED",

            "DISABLED",

            "WAITING",

            "TRIGGERED"
        ]

    def mark_waiting(
        self,
        symbol,
        liquidity
    ):

        self.set_state(
            symbol,
            liquidity,
            "WAITING"
        )

    def mark_triggered(
        self,
        symbol,
        liquidity
    ):

        self.set_state(
            symbol,
            liquidity,
            "TRIGGERED"
        )

    def mark_disabled(
        self,
        symbol,
        liquidity
    ):

        self.set_state(
            symbol,
            liquidity,
            "DISABLED"
        )

    def mark_consumed(
        self,
        symbol,
        liquidity
    ):

        self.set_state(
            symbol,
            liquidity,
            "CONSUMED"
        )