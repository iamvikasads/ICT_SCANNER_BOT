from alerts.telegram_client import (
    TelegramClient
)


def run_test():

    telegram = TelegramClient()

    message = (
        "ICT Scanner Bot\n\n"
        "Telegram Test Successful"
    )

    result = telegram.send_message(
        message
    )

    print(result)


if __name__ == "__main__":
    run_test()