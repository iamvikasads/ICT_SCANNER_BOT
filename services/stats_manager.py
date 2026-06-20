import json
import os


class StatsManager:

    FILE = "data/stats.json"

    DEFAULT = {

        # Strategy 1
        "s1_symbols_scanned": 0,
        "s1_sweeps_found": 0,
        "s1_entries_triggered": 0,
        "s1_expired": 0,
        "s1_invalidated": 0,

        # Strategy 2
        "s2_symbols_scanned": 0,
        "s2_mss_found": 0,
        "s2_ob_found": 0,
        "s2_setups_saved": 0,
        "s2_entries_triggered": 0,
        "s2_expired": 0,
        "s2_invalidated": 0,

        # Strategy 3
        "s3_symbols_scanned": 0,
        "s3_mss_found": 0,
        "s3_fvg_found": 0,
        "s3_setups_saved": 0,
        "s3_entries_triggered": 0,
        "s3_expired": 0,
        "s3_invalidated": 0,

        # Strategy 4
        "s4_sweeps_found": 0,
        "s4_mss_found": 0,
        "s4_liquidity_found": 0,
        "s4_entries_triggered": 0,
        "s4_invalidated": 0
    }

    @classmethod
    def load(cls):

        if not os.path.exists(cls.FILE):

            os.makedirs("data", exist_ok=True)

            with open(cls.FILE, "w") as f:
                json.dump(cls.DEFAULT, f, indent=4)

            return cls.DEFAULT.copy()

        with open(cls.FILE, "r") as f:
            return json.load(f)

    @classmethod
    def save(cls, data):

        with open(cls.FILE, "w") as f:
            json.dump(data, f, indent=4)

    @classmethod
    def increment(cls, key):

        data = cls.load()

        if key not in data:
            data[key] = 0

        data[key] += 1

        cls.save(data)

    @classmethod
    def reset(cls):

        cls.save(cls.DEFAULT.copy())