from alerts.telegram_client import TelegramClient

telegram = TelegramClient()

telegram.send_message(
    "✅ REAL TEST ALERT\n\nIf you receive this, Telegram delivery is working."
)

print("Done")