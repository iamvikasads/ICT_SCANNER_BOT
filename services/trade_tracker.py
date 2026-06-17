import time
from datetime import datetime

from core.binance.downloader import OHLCVDownloader
from core.storage.trade_logger import TradeLogger
from alerts.discord_client import DiscordClient


class TradeTracker:

    def __init__(self, downloader=None):
        # Accept shared downloader
        self.downloader = downloader or OHLCVDownloader()
        self.logger = TradeLogger()
        self.discord = DiscordClient()

    def check_trade(self, trade):

        try:

            symbol = trade["symbol"]
            direction = trade["direction"]
            entry = float(trade["entry"])
            sl = float(trade["sl"])
            tp = float(trade["tp"])
            rr = float(trade["rr"])
            trade_id = trade["trade_id"]
            open_time_str = trade["open_time"]

            # FIX: Fetch all 15m candles from open_time onwards
            # instead of only the last 5 (75 min)
            try:
                open_dt = datetime.strptime(open_time_str, "%Y-%m-%d %H:%M:%S")
                minutes_since_open = int(
                    (datetime.now() - open_dt).total_seconds() / 60
                )
                # Each 15m candle = 15 min; add 10 candles buffer
                candles_needed = max(10, (minutes_since_open // 15) + 10)
                candles_needed = min(candles_needed, 500)
            except Exception:
                candles_needed = 100

            candles = self.downloader.get_ohlcv(
                symbol=symbol,
                interval="15m",
                limit=candles_needed
            )

            # Only check candles after trade open_time
            try:
                open_ts_ms = int(
                    datetime.strptime(open_time_str, "%Y-%m-%d %H:%M:%S")
                    .timestamp() * 1000
                )
            except Exception:
                open_ts_ms = 0

            relevant = [
                c for c in candles
                if c["timestamp"] > open_ts_ms
            ]

            if not relevant:
                print(f"{symbol} -> No candles since open, still OPEN")
                return

            for candle in relevant:

                high = candle["high"]
                low = candle["low"]
                ts = candle["timestamp"]

                if direction == "LONG":
                    sl_hit = low <= sl
                    tp_hit = high >= tp

                    if sl_hit:
                        self._close_trade(trade_id, symbol, trade, entry, sl, tp, rr, "LOSS", ts)
                        return

                    if tp_hit:
                        self._close_trade(trade_id, symbol, trade, entry, sl, tp, rr, "WIN", ts)
                        return

                else:
                    sl_hit = high >= sl
                    tp_hit = low <= tp

                    if sl_hit:
                        self._close_trade(trade_id, symbol, trade, entry, sl, tp, rr, "LOSS", ts)
                        return

                    if tp_hit:
                        self._close_trade(trade_id, symbol, trade, entry, sl, tp, rr, "WIN", ts)
                        return

            print(f"{symbol} -> Still OPEN")

        except Exception as e:
            print(f"[TRACKER ERROR] {trade.get('symbol', '?')}: {e}")

    def _close_trade(self, trade_id, symbol, trade, entry, sl, tp, rr, result, ts):

        close_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.update_trade(trade_id, result, close_time)

        if result == "WIN":
            emoji = "✅"
            level_label = "TP"
            level = tp
            r_label = f"+{rr}R"
        else:
            emoji = "❌"
            level_label = "SL"
            level = sl
            r_label = "-1R"

        message = (
            f"{emoji} {result}\n"
            f"{'─' * 22}\n"
            f"Pair:      {symbol}\n"
            f"Strategy:  {trade['strategy']}\n"
            f"Direction: {trade['direction']}\n"
            f"{'─' * 22}\n"
            f"Entry:  {entry}\n"
            f"{level_label}:     {level}\n"
            f"{'─' * 22}\n"
            f"Result: {r_label}"
        )

        self.discord.send_trade(message)
        print(f"[{result}] {symbol} {r_label}")

    def run(self):

        trades = self.logger.get_open_trades()

        if not trades:
            print("\n[TRACKER] No Open Trades\n")
            return

        print(f"\n[TRACKER] Checking {len(trades)} Open Trades\n")

        for trade in trades:
            self.check_trade(trade)
            time.sleep(0.2)