#!/usr/bin/env python3
"""
EMA ALERT BOT V1

Entry point of the application.
"""

from core.logger import get_logger
from scanner.scanner import run_forever

from alerts.telegram import (
    send_shutdown_message,
    send_crash_message,
)

log = get_logger(__name__)


def main():
    """
    Start EMA Alert Bot.
    """

    try:

        run_forever()

    except KeyboardInterrupt:

        log.info("Shutdown requested by user.")

        send_shutdown_message()

        print("\nEMA Alert Bot stopped by user.\n")

    except Exception as exc:

        log.exception("Unexpected fatal error.")

        send_crash_message(exc)

        raise


if __name__ == "__main__":

    main()