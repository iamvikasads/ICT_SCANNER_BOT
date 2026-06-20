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
            
            original_sl = float(
                trade["original_sl"]
            )

            be_moved = (
                trade["be_moved"] == "YES"
            )

            one_r_locked = (
                trade["one_r_locked"] == "YES"
            )

            # FIX: Fetch all 30m candles from open_time onwards
            # instead of only the last 5 (75 min)
            try:
                open_dt = datetime.strptime(open_time_str, "%Y-%m-%d %H:%M:%S")
                minutes_since_open = int(
                    (datetime.now() - open_dt).total_seconds() / 60
                )
                # Each 30m candle = 30 min; add 10 candles buffer
                candles_needed = max(10, (minutes_since_open // 30) + 10)
                candles_needed = min(candles_needed, 500)
            except Exception:
                candles_needed = 100

            candles = self.downloader.get_ohlcv(
                symbol=symbol,
                interval="30m",
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

            risk = abs(
                entry - original_sl
            )

            if direction == "LONG":

                one_r_price = (
                    entry + risk
                )

            else:

                one_r_price = (
                    entry - risk
                )

            if direction == "LONG":

                two_r_price = (
                    entry + (risk * 2)
                )

            else:

                two_r_price = (
                    entry - (risk * 2)
                )

            for candle in relevant:

                high = candle["high"]
                low = candle["low"]
                ts = candle["timestamp"]

                if not be_moved:

                    if direction == "LONG":

                        if high >= one_r_price:

                            self.logger.update_sl(
                                trade_id,
                                entry
                            )

                            self.logger.mark_breakeven(
                                trade_id
                            )

                            self.discord.send_trade(

                                f"🔒 BREAKEVEN MOVED\n"
                                f"{symbol}\n"
                                f"{direction}\n"
                                f"New SL: {entry}"

                            )

                            print(
                                f"[BE] {symbol}"
                            )

                            be_moved = True
                            sl = entry

                        if (
                            be_moved
                            and
                            not one_r_locked
                        ):

                            if high >= two_r_price:

                                self.logger.update_sl(
                                    trade_id,
                                    entry + risk
                                )

                                self.logger.mark_one_r_locked(
                                    trade_id
                                )

                                one_r_locked = True
                                sl = entry + risk

                                print(
                                    f"[+1R LOCKED] {symbol}"
                                )

                    else:

                        if low <= one_r_price:

                            self.logger.update_sl(
                                trade_id,
                                entry
                            )

                            self.logger.mark_breakeven(
                                trade_id
                            )

                            self.discord.send_trade(

                                f"🔒 BREAKEVEN MOVED\n"
                                f"{symbol}\n"
                                f"{direction}\n"
                                f"New SL: {entry}"

                            )

                            print(
                                f"[BE] {symbol}"
                            )

                            be_moved = True
                            sl = entry

                        if (
                            be_moved
                            and
                            not one_r_locked
                        ):

                            if low <= two_r_price:

                                self.logger.update_sl(
                                    trade_id,
                                    entry - risk
                                )

                                self.logger.mark_one_r_locked(
                                    trade_id
                                )

                                one_r_locked = True
                                sl = entry - risk

                                print(
                                    f"[+1R LOCKED] {symbol}"
                                )

                if direction == "LONG":
                    sl_hit = low <= sl
                    tp_hit = high >= tp

                    if tp_hit:
                        self._close_trade(
                            trade_id,
                            symbol,
                            trade,
                            entry,
                            sl,
                            tp,
                            rr,
                            "WIN",
                            ts
                        )
                        return

                    if sl_hit:
                    
                        if one_r_locked:
                        
                            self._close_trade(
                                trade_id,
                                symbol,
                                trade,
                                entry,
                                sl,
                                tp,
                                rr,
                                "LOCKED_1R",
                                ts
                            )
                            
                        elif be_moved:
                        
                            self._close_trade(
                                trade_id,
                                symbol,
                                trade,
                                entry,
                                sl,
                                tp,
                                rr,
                                "BREAKEVEN",
                                ts
                            )
                        
                        else:
                        
                            self._close_trade(
                                trade_id,
                                symbol,
                                trade,
                                entry,
                                sl,
                                tp,
                                rr,
                                "LOSS",
                                ts
                            )
                        
                        return

                else:
                    sl_hit = high >= sl
                    tp_hit = low <= tp

                    if tp_hit:
                        self._close_trade(
                            trade_id,
                            symbol,
                            trade,
                            entry,
                            sl,
                            tp,
                            rr,
                            "WIN",
                            ts
                        )
                        return

                    if sl_hit:
                    
                        if one_r_locked:
                        
                            self._close_trade(
                                trade_id,
                                symbol,
                                trade,
                                entry,
                                sl,
                                tp,
                                rr,
                                "LOCKED_1R",
                                ts
                            )
                            
                        elif be_moved:
                        
                            self._close_trade(
                                trade_id,
                                symbol,
                                trade,
                                entry,
                                sl,
                                tp,
                                rr,
                                "BREAKEVEN",
                                ts
                            )
                        
                        else:
                        
                            self._close_trade(
                                trade_id,
                                symbol,
                                trade,
                                entry,
                                sl,
                                tp,
                                rr,
                                "LOSS",
                                ts
                            )
                        
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

        elif result == "LOCKED_1R":

            emoji = "💰"
            level_label = "LOCKED"
            level = sl
            r_label = "+1R"

        elif result == "BREAKEVEN":

            emoji = "🔒"
            level_label = "BE"
            level = entry
            r_label = "0R"

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