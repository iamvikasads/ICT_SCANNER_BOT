import time

from core.binance.downloader import OHLCVDownloader
from core.storage.strategy3_logger import Strategy3Logger
from core.storage.trade_logger import TradeLogger
from core.risk.risk_engine import RiskEngine
from strategies.fvg.touch_scanner import FVGTouchScanner
from core.filters.daily_bias import DailyBiasFilter

from alerts.telegram_client import TelegramClient
from alerts.message_builder import MessageBuilder


class Strategy3EntryScanner:

    VALID_CANDLES = 10

    def __init__(self, downloader=None):
        self.downloader = downloader or OHLCVDownloader()
        self.logger = Strategy3Logger()
        self.trade_logger = TradeLogger()
        self.risk_engine = RiskEngine()
        self.touch_scanner = FVGTouchScanner()
        self.bias_filter = DailyBiasFilter()
        
        self.telegram = TelegramClient()
        self.message_builder = MessageBuilder()

    def process_setup(self, setup):

        try:

            symbol = setup["symbol"]
            direction = setup["direction"]
            setup_timestamp = int(setup["timestamp"])
            fvg_high = float(setup["fvg_high"])
            fvg_low = float(setup["fvg_low"])

            
            #(symbol, direction):
                #print(f"{symbol} -> Daily bias against {direction} (IGNORED)")

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
                if direction == "LONG" and candle["close"] < fvg_low:
                    self.logger.update_status(setup["setup_id"], "INVALIDATED")
                    print(f"{symbol} -> FVG INVALIDATED")
                    return
                if direction == "SHORT" and candle["close"] > fvg_high:
                    self.logger.update_status(setup["setup_id"], "INVALIDATED")
                    print(f"{symbol} -> FVG INVALIDATED")
                    return

            candles_1h = self.downloader.get_ohlcv(
                symbol=symbol, interval="1h", limit=50
            )

            candle = candles_1h[-2]
            touch_result = self.touch_scanner.check_touch(setup, candle)

            if touch_result is None:
                
                return

            risk = self.risk_engine.fvg(
                direction=direction,
                entry=candle["close"],
                fvg_high=fvg_high,
                fvg_low=fvg_low
            )

            if risk is None:
                print(f"{symbol} -> Invalid risk")
                return

            entry_data = {
                "setup_id": setup["setup_id"],
                "timestamp": candle["timestamp"],
                "symbol": symbol,
                "strategy": "MSS + FVG",
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

            print(f"[S3 ENTRY] {symbol} {direction} Entry={risk['entry']}")

        except Exception as e:
            print(f"[S3 ENTRY ERROR] {setup['symbol']}: {e}")

    def run(self):

        setups = self.logger.get_waiting_setups()

        if not setups:
            print("\n[S3] No Waiting Setups\n")
            return

        print(f"\n[S3] Checking {len(setups)} Waiting Setups\n")

        for setup in setups:
            self.process_setup(setup)
            time.sleep(0.2)
