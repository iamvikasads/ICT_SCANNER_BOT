import csv
import os


class SweepLogger:

    def __init__(self):
        self.file_path = "data/sweeps.csv"
        self.ensure_file_exists()

    def ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            os.makedirs("data", exist_ok=True)
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([
                    "timestamp", "symbol", "direction", "liquidity", "status"
                ])

    # FIX: Now checks direction too — LONG and SHORT on same candle can both save
    def sweep_exists(self, timestamp, symbol, direction):
        self.ensure_file_exists()
        with open(self.file_path, "r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if (
                    row["timestamp"] == str(timestamp)
                    and row["symbol"] == symbol
                    and row["direction"] == direction
                    and row["status"] == "WAITING"
                ):
                    return True
        return False

    def save_sweep(self, timestamp, symbol, direction, liquidity, status="WAITING"):
        self.ensure_file_exists()
        with open(self.file_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([timestamp, symbol, direction, liquidity, status])

    def get_waiting_sweeps(self):
        self.ensure_file_exists()
        sweeps = []
        with open(self.file_path, "r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["status"] == "WAITING":
                    sweeps.append(row)
        return sweeps

    def update_status(self, timestamp, symbol, new_status):
        self.ensure_file_exists()
        rows = []
        with open(self.file_path, "r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if (
                    row["timestamp"] == str(timestamp)
                    and row["symbol"] == symbol
                ):
                    row["status"] = new_status
                rows.append(row)

        with open(self.file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "timestamp", "symbol", "direction", "liquidity", "status"
            ])
            writer.writeheader()
            writer.writerows(rows)
