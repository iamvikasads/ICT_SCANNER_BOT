from core.storage.trade_logger import TradeLogger
from alerts.telegram_client import TelegramClient


class DailySummary:

    def __init__(self):
        self.trade_logger = TradeLogger()
        self.telegram = TelegramClient()

    def send(self, setups_found=0, entries_fired=0, errors=0):

        try:
            stats = self.trade_logger.get_daily_stats()

            wins = stats["wins"]
            losses = stats["losses"]
            open_trades = stats["open"]
            total_closed = wins + losses

            winrate = (
                round((wins / total_closed) * 100)
                if total_closed > 0 else 0
            )

            status_line = (
                "✅ No errors today"
                if errors == 0
                else f"⚠️ {errors} error(s) occurred"
            )

            message = (
                f"📊 DAILY SUMMARY\n"
                f"{'─' * 22}\n"
                f"Setups found:  {setups_found}\n"
                f"Entries fired: {entries_fired}\n"
                f"{'─' * 22}\n"
                f"Wins:   {wins}\n"
                f"Losses: {losses}\n"
                f"Winrate: {winrate}%\n"
                f"Open:   {open_trades}\n"
                f"{'─' * 22}\n"
                f"{status_line}"
            )

            self.telegram.send_message(message)

        except Exception as e:
            print(f"[SUMMARY ERROR] {e}")
