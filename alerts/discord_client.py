import os
import requests
from dotenv import load_dotenv
load_dotenv()
class DiscordClient:

    def __init__(self):

        self.status_webhook = os.getenv(
            "STATUS_WEBHOOK"
        )

        self.setup_webhook = os.getenv(
            "SETUP_WEBHOOK"
        )

        self.entry_webhook = os.getenv(
            "ENTRY_WEBHOOK"
        )

        self.trade_webhook = os.getenv(
            "TRADE_WEBHOOK"
        )

        self.error_webhook = os.getenv(
            "ERROR_WEBHOOK"
        )

    def _send(
        self,
        webhook,
        message
    ):

        try:

            if not webhook:

                print(
                    "[DISCORD ERROR] Webhook not configured"
                )

                return

            response = requests.post(

                webhook,

                json={
                    "content": message
                },

                timeout=10

            )

            print(
                f"[DISCORD] {response.status_code}"
            )

        except Exception as e:

            print(
                f"[DISCORD ERROR] {e}"
            )

    def send_status(
        self,
        message
    ):

        self._send(
            self.status_webhook,
            message
        )

    def send_setup(
        self,
        message
    ):

        self._send(
            self.setup_webhook,
            message
        )

    def send_entry(
        self,
        message
    ):

        self._send(
            self.entry_webhook,
            message
        )

    def send_trade(
        self,
        message
    ):

        self._send(
            self.trade_webhook,
            message
        )

    def send_error(
        self,
        message
    ):

        self._send(
            self.error_webhook,
            message
        )