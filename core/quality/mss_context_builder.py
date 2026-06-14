class MSSContextBuilder:

    def __init__(self):
        pass

    # ==================================
    # BUILD MSS CONTEXT
    # ==================================

    def build(
        self,
        candles_4h,
        candles_1h,
        mss_result
    ):

        if (
            mss_result is None
            or
            mss_result.get("mss") is None
        ):

            return None

        mss_timestamp = (
            mss_result["timestamp"]
        )

        mss_direction = (
            mss_result["mss"]
        )

        # ==========================
        # FIND MSS LOCATION INSIDE
        # 1H DATASET
        # ==========================

        mss_index_1h = None

        for i, candle in enumerate(
            candles_1h
        ):

            if (
                candle["timestamp"]
                >= mss_timestamp
            ):

                mss_index_1h = i
                break

        if (
            mss_index_1h
            is None
        ):

            return None

        # ==========================
        # SEARCH WINDOW
        # ==========================

        search_start = max(
            0,
            mss_index_1h - 20
        )

        search_end = (
            mss_index_1h
        )

        return {

            "direction":
                mss_direction,

            "mss_timestamp":
                mss_timestamp,

            "mss_index_1h":
                mss_index_1h,

            "search_start":
                search_start,

            "search_end":
                search_end
        }

    # ==================================
    # FILTER 1H CANDLES
    # ==================================

    def get_search_candles(
        self,
        candles_1h,
        context
    ):

        if context is None:
            return []

        return candles_1h[

            context["search_start"]:

            context["search_end"]

        ]