import csv
import os


class Strategy3Logger:

    def __init__(self):
        self.setup_file = "data/strategy3_setups.csv"
        self.entry_file = "data/strategy3_entries.csv"
        self.ensure_files_exist()

    def ensure_files_exist(self):

        if not os.path.exists(self.setup_file):
            with open(self.setup_file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([
                    "setup_id", "timestamp", "symbol", "strategy",
                    "direction", "fvg_high", "fvg_low", "status"
                ])

        if not os.path.exists(self.entry_file):
            with open(self.entry_file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([
                    "setup_id", "timestamp", "symbol", "strategy",
                    "direction", "entry", "sl", "tp", "rr"
                ])

    # FIX: setup_exists now checks direction too (was symbol-only)
    def setup_exists(self, symbol, direction):

        with open(self.setup_file, "r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if (
                    row["symbol"] == symbol
                    and row["direction"] == direction
                    and row["status"] == "WAITING"
                ):
                    return True
        return False

    def save_setup(self, setup_data):
        with open(self.setup_file, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                setup_data["setup_id"],
                setup_data["timestamp"],
                setup_data["symbol"],
                setup_data["strategy"],
                setup_data["direction"],
                setup_data["fvg_high"],
                setup_data["fvg_low"],
                setup_data["status"]
            ])

    def get_waiting_setups(self):
        setups = []
        with open(self.setup_file, "r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["status"] == "WAITING":
                    setups.append(row)
        return setups

    def update_status(self, setup_id, status):
        rows = []
        with open(self.setup_file, "r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["setup_id"] == setup_id:
                    row["status"] = status
                rows.append(row)

        with open(self.setup_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "setup_id", "timestamp", "symbol", "strategy",
                "direction", "fvg_high", "fvg_low", "status"
            ])
            writer.writeheader()
            writer.writerows(rows)

    def save_entry(self, entry_data):
        with open(self.entry_file, "a", newline="", encoding="utf-8") as f:
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
