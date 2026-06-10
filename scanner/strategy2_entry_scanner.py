import time

from core.binance.downloader import OHLCVDownloader
from core.storage.strategy2_logger import Strategy2Logger
from core.storage.trade_logger import TradeLogger
from strategies.extreme_ob.touch_scanner import TouchScanner
from core.risk.risk_engine import RiskEngine
from core.filters.daily_bias import DailyBiasFilter

from alerts.telegram_client import TelegramClient
from alerts.message_builder import MessageBuilder


class Strategy2EntryScanner:

    VALID_CANDLES = 10

    def __init__(self, downloader=None):
        self.downloader = downloader or OHLCVDownloader()
        self.logger = Strategy2Logger()
        self.trade_logger = TradeLogger()
        self.touch_scanner = TouchScanner()
        self.risk_engine = RiskEngine()
        self.bias_filter = DailyBiasFilter()
       
        self.telegram = TelegramClient()
        self.message_builder = MessageBuilder()

    def process_setup(self, setup):

        try:

            symbol = setup["symbol"]
            direction = setup["direction"]
            setup_timestamp = int(setup["timestamp"])
            ob_high = float(setup["ob_high"])
            ob_low = float(setup["ob_low"])

            

            if not self.bias_filter.allows_direction(symbol, direction):
                print(f"{symbol} -> Daily bias against {direction}, skipping")
                return

            candles_4h = self.downloader.get_ohlcv(
                symbol=symbol, interval="4h", limit=20
            )

            candles_after = sum(
                1 for c in candles_4h if c["timestamp"] > setup_timestamp
            )

            if candles_after > self.VALID_CANDLES:
                self.logger.update_status(setup["setup_id"], "EXPIRED")
                print(f"{symbol} -> Setup EXPIRED")
                return

            for candle in candles_4h:
                if candle["timestamp"] <= setup_timestamp:
                    continue
                if direction == "LONG" and candle["close"] < ob_low:
                    self.logger.update_status(setup["setup_id"], "INVALIDATED")
                    print(f"{symbol} -> OB INVALIDATED")
                    return
                if direction == "SHORT" and candle["close"] > ob_high:
                    self.logger.update_status(setup["setup_id"], "INVALIDATED")
                    print(f"{symbol} -> OB INVALIDATED")
                    return

            candles_1h = self.downloader.get_ohlcv(
                symbol=symbol, interval="1h", limit=50
            )

            candle_1h = candles_1h[-2]
            touch_result = self.touch_scanner.check_touch(setup, candle_1h)

            print(
                f"{symbol} | Close={candle_1h['close']} "
                f"OB={ob_low}-{ob_high}"
            )

            if touch_result is None:
                print(f"{symbol} -> No Entry Trigger")
                return

            risk = self.risk_engine.extreme_ob(
                direction=direction,
                entry=candle_1h["close"],
                ob_high=ob_high,
                ob_low=ob_low
            )

            if risk is None:
                print(f"{symbol} -> Invalid risk")
                return

            entry_data = {
                "setup_id": setup["setup_id"],
                "timestamp": candle_1h["timestamp"],
                "symbol": symbol,
                "strategy": setup["strategy"],
                "direction": direction,
                "entry": risk["entry"],
                "sl": risk["sl"],
                "tp": risk["tp"],
                "rr": risk["rr"]
            }

            self.logger.save_entry(entry_data)
            self.trade_logger.save_trade(entry_data)
            self.logger.update_status(setup["setup_id"], "TRIGGERED")

            message = self.message_builder.build_entry_message(entry_data)
            self.telegram.send_message(message)

            print(f"[S2 ENTRY] {symbol} {direction} Entry={risk['entry']}")

        except Exception as e:
            print(f"[S2 ENTRY ERROR] {setup['symbol']}: {e}")

    def run(self):

        setups = self.logger.get_waiting_setups()

        if not setups:
            print("\n[S2] No Waiting Setups\n")
            return

        print(f"\n[S2] Checking {len(setups)} Waiting Setups\n")

        for setup in setups:
            self.process_setup(setup)
            time.sleep(0.2)
