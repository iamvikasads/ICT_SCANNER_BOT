from core.storage.trade_logger import TradeLogger
from alerts.discord_client import DiscordClient
from services.stats_manager import StatsManager


class DailySummary:

    def __init__(self):
        self.trade_logger = TradeLogger()
        self.discord = DiscordClient()

    def send(self, setups_found=0, entries_fired=0, errors=0):

        try:

            trade_stats = self.trade_logger.get_daily_stats()
            stats = StatsManager.load()

            wins = trade_stats["wins"]

            losses = trade_stats["losses"]

            breakevens = trade_stats["breakevens"]

            locked_1r = trade_stats["locked_1r"]

            open_trades = trade_stats["open"]

            open_trade_details = (
                self.trade_logger
                .get_open_trade_details()
            )

            open_section = ""

            for trade in open_trade_details:

                open_section += (

                    f"\n{trade['symbol']} "
                    f"{trade['direction']}\n"

                    f"Entry: {trade['entry']}\n"

                    f"SL: {trade['sl']}\n"

                    f"BE: {trade['be_moved']}\n"

                    f"+1R: {trade['one_r_locked']}\n"
                )

            total_closed = wins + losses

            winrate = (
                round((wins / total_closed) * 100)
                if total_closed > 0
                else 0
            )

            status_line = (
                "✅ No errors today"
                if errors == 0
                else f"⚠️ {errors} error(s) occurred"
            )

            message = (

                f"📊 DAILY SUMMARY\n"
                f"{'─' * 25}\n"

                f"STRATEGY 1\n"
                f"Scanned:     {stats['s1_symbols_scanned']}\n"
                f"Sweeps:      {stats['s1_sweeps_found']}\n"
                f"Triggered:   {stats['s1_entries_triggered']}\n"
                f"Expired:     {stats['s1_expired']}\n"
                f"Invalidated: {stats['s1_invalidated']}\n"

                f"{'─' * 25}\n"

                f"STRATEGY 2\n"
                f"Scanned:     {stats['s2_symbols_scanned']}\n"
                f"MSS:         {stats['s2_mss_found']}\n"
                f"OB:          {stats['s2_ob_found']}\n"
                f"Setups:      {stats['s2_setups_saved']}\n"
                f"Triggered:   {stats['s2_entries_triggered']}\n"
                f"Expired:     {stats['s2_expired']}\n"
                f"Invalidated: {stats['s2_invalidated']}\n"

                f"{'─' * 25}\n"

                f"STRATEGY 3\n"
                f"Scanned:     {stats['s3_symbols_scanned']}\n"
                f"MSS:         {stats['s3_mss_found']}\n"
                f"FVG:         {stats['s3_fvg_found']}\n"
                f"Setups:      {stats['s3_setups_saved']}\n"
                f"Triggered:   {stats['s3_entries_triggered']}\n"
                f"Expired:     {stats['s3_expired']}\n"
                f"Invalidated: {stats['s3_invalidated']}\n"

                f"{'─' * 25}\n"

                f"STRATEGY 4\n"
                f"Sweeps:      {stats['s4_sweeps_found']}\n"
                f"MSS:         {stats['s4_mss_found']}\n"
                f"Liquidity:   {stats['s4_liquidity_found']}\n"
                f"Triggered:   {stats['s4_entries_triggered']}\n"
                f"Invalidated: {stats['s4_invalidated']}\n"

                f"{'─' * 25}\n"

                f"WINS:        {wins}\n"
                f"LOSSES:      {losses}\n"
                f"BREAKEVEN:   {breakevens}\n"
                f"LOCKED +1R:  {locked_1r}\n"
                f"WINRATE:     {winrate}%\n"
                f"OPEN:        {open_trades}\n"

                f"{'─' * 25}\n"

                f"OPEN TRADE STATUS\n"

                f"{open_section}"

                f"{'─' * 25}\n"

                f"{status_line}"
            )

            self.discord.send_status(message)

            # Reset stats after successful summary
            StatsManager.reset()

        except Exception as e:

            print(f"[SUMMARY ERROR] {e}")