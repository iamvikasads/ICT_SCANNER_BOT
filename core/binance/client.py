from binance.client import Client

from config.settings import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET
)

from config.symbols import TOP_25_SYMBOLS


class BinanceClient:

    def __init__(self):

        self.client = Client(
            BINANCE_API_KEY,
            BINANCE_API_SECRET,
            requests_params={
                "timeout": 20
            }
        )

    def get_top_25_symbols(self):

        return TOP_25_SYMBOLS