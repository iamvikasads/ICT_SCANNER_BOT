from datetime import datetime, timezone


class SessionFilter:
    """
    ICT Kill Zones (UTC):
    - London Open:   07:00 - 10:00
    - New York Open: 13:00 - 16:00
    - Daily Open:    00:00 - 01:00

    Only allow entries during these windows.
    """

    KILL_ZONES = [
        (0, 1),    # Daily Open
        (7, 10),   # London Open
        (13, 16),  # New York Open
    ]

    def is_active(self):
        now_utc = datetime.now(timezone.utc)
        hour = now_utc.hour
        for start, end in self.KILL_ZONES:
            if start <= hour < end:
                return True
        return False

    def current_session(self):
        now_utc = datetime.now(timezone.utc)
        hour = now_utc.hour
        if 0 <= hour < 1:
            return "Daily Open"
        if 7 <= hour < 10:
            return "London Open"
        if 13 <= hour < 16:
            return "New York Open"
        return "Off-session"
