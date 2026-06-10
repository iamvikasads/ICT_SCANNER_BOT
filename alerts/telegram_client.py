import requests

from config.settings import (
    TELEGRAM_BOT_TOKEN
)


class TelegramClient:

    def __init__(self):

        self.token = TELEGRAM_BOT_TOKEN

        self.url = (
            f"https://api.telegram.org/bot"
            f"{self.token}/sendMessage"
        )

    def get_chat_ids(self):

        chat_ids = []

        try:

            with open(
                "data/chat_ids.txt",
                "r",
                encoding="utf-8"
            ) as file:

                for line in file:

                    chat_id = line.strip()

                    if chat_id:

                        chat_ids.append(
                            chat_id
                        )

        except FileNotFoundError:

            print(
                "[TELEGRAM] "
                "chat_ids.txt not found"
            )

        return chat_ids

    def send_message(
        self,
        message
    ):

        chat_ids = (
            self.get_chat_ids()
        )

        if not chat_ids:

            return

        for chat_id in chat_ids:

            try:

                payload = {

                    "chat_id": chat_id,

                    "text": message
                }

                requests.post(
                    self.url,
                    data=payload,
                    timeout=10
                )

            except Exception as e:

                print(
                    f"[TELEGRAM ERROR] "
                    f"{chat_id} -> {e}"
                )