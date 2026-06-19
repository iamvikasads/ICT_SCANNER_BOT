import csv
import os
import time
from datetime import datetime


class TradeLogger:

    MAX_OPEN_TRADES = 5

    def __init__(self):
        self.trade_file = "data/trades.csv"
        self._initialize()

    def _initialize(self):
        if not os.path.exists(self.trade_file):
            os.makedirs("data", exist_ok=True)
            with open(self.trade_file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([
                    "trade_id", "setup_id", "symbol", "strategy",
                    "direction", "entry", "sl", "tp", "rr",
                    "status", "result", "open_time", "close_time"
                ])

    def _count_open_trades(self):
        count = 0
        with open(self.trade_file, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["status"] == "OPEN":
                    count += 1
        return count

    def has_open_trade(self, symbol, strategy):
        with open(self.trade_file, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if (
                    row["symbol"] == symbol
                    and row["strategy"] == strategy
                    and row["status"] == "OPEN"
                ):
                    return True
        return False

    def save_trade(self, entry_data):

        if self.has_open_trade(entry_data["symbol"], entry_data["strategy"]):
            print(f"[SKIP] Open trade exists -> {entry_data['symbol']}")
            return False

        # FIX: Check global open trade cap
        open_count = self._count_open_trades()
        if open_count >= self.MAX_OPEN_TRADES:
            print(
                f"[SKIP] Max open trades reached "
                f"({open_count}/{self.MAX_OPEN_TRADES}) -> {entry_data['symbol']}"
            )
            return False

        # FIX: Generate proper unique trade_id separate from setup_id
        trade_id = f"TRD_{entry_data['symbol']}_{int(time.time())}"
        open_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.trade_file, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                trade_id,
                entry_data["setup_id"],
                entry_data["symbol"],
                entry_data["strategy"],
                entry_data["direction"],
                entry_data["entry"],
                entry_data["sl"],
                entry_data["tp"],
                entry_data["rr"],
                "OPEN",
                "",
                open_time,
                ""
            ])

        return True

    def get_open_trades(self):
        trades = []
        with open(self.trade_file, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["status"] == "OPEN":
                    trades.append(row)
        return trades

    def update_trade(self, trade_id, result, close_time=None):
        if close_time is None:
            close_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        rows = []
        with open(self.trade_file, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["trade_id"] == trade_id:
                    row["status"] = "CLOSED"
                    row["result"] = result
                    row["close_time"] = close_time
                rows.append(row)

        with open(self.trade_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "trade_id", "setup_id", "symbol", "strategy",
                "direction", "entry", "sl", "tp", "rr",
                "status", "result", "open_time", "close_time"
            ])
            writer.writeheader()
            writer.writerows(rows)

    def get_daily_stats(self):
        from datetime import datetime, timedelta

        report_day = (
            datetime.utcnow().date()
            - timedelta(days=1)
        ).strftime("%Y-%m-%d")
        wins = losses = open_count = 0
        with open(self.trade_file, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["status"] == "OPEN":
                    open_count += 1
                if row["close_time"].startswith(report_day):
                    if row["result"] == "WIN":
                        wins += 1
                    elif row["result"] == "LOSS":
                        losses += 1
        return {"wins": wins, "losses": losses, "open": open_count}