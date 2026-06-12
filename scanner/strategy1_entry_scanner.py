import time

from core.binance.client import BinanceClient
from core.binance.downloader import OHLCVDownloader
from strategies.turtle_soup.detector import TurtleSoupDetector
from core.storage.sweep_logger import SweepLogger
from core.storage.csv_logger import CSVLogger
from core.storage.trade_logger import TradeLogger
from core.risk.risk_engine import RiskEngine

from core.filters.daily_bias import DailyBiasFilter
from alerts.telegram_client import TelegramClient
from alerts.message_builder import MessageBuilder


class Strategy1EntryScanner:

    VALID_CANDLES = 3

    def __init__(self, downloader=None):
        self.client = BinanceClient()
        self.downloader = downloader or OHLCVDownloader()
        self.detector = TurtleSoupDetector()
        self.sweep_logger = SweepLogger()
        self.csv_logger = CSVLogger()
        self.trade_logger = TradeLogger()
        self.risk_engine = RiskEngine()
        
        self.bias_filter = DailyBiasFilter()
        self.telegram = TelegramClient()
        self.message_builder = MessageBuilder()

    def process_sweep(self, sweep):

        try:

            symbol = sweep["symbol"]
            sweep_timestamp = int(sweep["timestamp"])
            direction = sweep["direction"]

            # SESSION FILTER
            
            # FIX: Daily bias filter now applied to S1 too
            #if not self.bias_filter.allows_direction(symbol, direction):
               # print(
                    #f"{symbol} -> Daily bias against "
                    #f"{direction} (IGNORED)"
               # )

            candles_1h = self.downloader.get_ohlcv(
                symbol=symbol,
                interval="1h",
                limit=100
            )

            # EXPIRY CHECK
            closed_after_sweep = sum(
                1 for c in candles_1h
                if c["timestamp"] > sweep_timestamp
            )

            if closed_after_sweep > self.VALID_CANDLES:
                self.sweep_logger.update_status(sweep_timestamp, symbol, "EXPIRED")
                print(f"{symbol} -> EXPIRED")
                return

            daily_levels = self.downloader.get_previous_day_levels(symbol)

            result = self.detector.detect(
                candles=candles_1h,
                pdh=daily_levels["pdh"],
                pdl=daily_levels["pdl"]
            )

            if result["signal"] is None:
                print(f"{symbol} -> WAITING")
                return

            entry = result["entry"]

            sweep_level = (
                daily_levels["pdl"] if direction == "LONG"
                else daily_levels["pdh"]
            )

            risk = self.risk_engine.turtle_soup(
                direction=direction,
                entry=entry,
                sweep_level=sweep_level
            )

            if risk is None:
                print(f"{symbol} -> Invalid risk")
                return

            entry_data = {
                "setup_id": f"{symbol}_TS_{candles_1h[-2]['timestamp']}",
                "timestamp": candles_1h[-2]["timestamp"],
                "symbol": symbol,
                "strategy": "TURTLE SOUP V2",
                "direction": direction,
                "entry": risk["entry"],
                "sl": risk["sl"],
                "tp": risk["tp"],
                "rr": risk["rr"]
            }

            self.csv_logger.log_entry(entry_data)
            self.trade_logger.save_trade(entry_data)
            self.csv_logger.log_signal({
                "timestamp": candles_1h[-2]["timestamp"],
                "symbol": symbol,
                "strategy": "TURTLE SOUP V2",
                "signal_type": "ENTRY"
            })

            message = self.message_builder.build_entry_message(entry_data)
            self.telegram.send_message(message)

            self.sweep_logger.update_status(sweep_timestamp, symbol, "TRIGGERED")

            print(f"[TS ENTRY] {symbol} {direction}")

        except Exception as e:
            print(f"[TS ENTRY ERROR] {sweep['symbol']}: {e}")

    def run(self):

        sweeps = self.sweep_logger.get_waiting_sweeps()

        if not sweeps:
            print("\n[TS] No Waiting Sweeps\n")
            return

        print(f"\n[TS] Checking {len(sweeps)} Waiting Sweeps\n")

        for sweep in sweeps:
            self.process_sweep(sweep)
            time.sleep(0.2)