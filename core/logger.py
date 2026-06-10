import logging
import os
from datetime import datetime


def setup_logger():

    os.makedirs("logs", exist_ok=True)

    log_file = f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger("ict_bot")


logger = setup_logger()
