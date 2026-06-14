class FVGRanker:

    def __init__(self):
        pass

    # ==================================
    # SCORE SINGLE FVG
    # ==================================

    def score_fvg(
        self,
        fvg,
        freshness_engine=None,
        candles=None
    ):

        score = 0

        # ==========================
        # FRESHNESS
        # ==========================

        freshness_score = 1

        if (
            freshness_engine
            and
            candles
        ):

            freshness_score = (
                freshness_engine.score(
                    fvg,
                    candles
                )
            )

            score += (
                freshness_score * 40
            )

        # ==========================
        # GAP SIZE
        # ==========================

        gap_size = abs(

            fvg["fvg_high"]
            -
            fvg["fvg_low"]

        )

        score += min(
            gap_size * 100,
            20
        )

        # ==========================
        # DISPLACEMENT
        # ==========================

        displacement = (
            fvg.get(
                "displacement_ratio",
                1
            )
        )

        score += min(
            displacement * 10,
            20
        )

        # ==========================
        # MSS DISTANCE
        # ==========================

        distance = (
            fvg.get(
                "distance_to_mss",
                10
            )
        )

        distance_score = max(
            0,
            15 - distance
        )

        score += distance_score

        # ==========================
        # SAVE SCORES
        # ==========================

        fvg["freshness_score"] = round(
            freshness_score,
            2
        )

        fvg["rank_score"] = round(
            score,
            2
        )

        return fvg

    # ==================================
    # SCORE ALL
    # ==================================

    def score_all(
        self,
        fvgs,
        freshness_engine=None,
        candles=None
    ):

        if not fvgs:
            return []

        ranked = []

        for fvg in fvgs:

            ranked.append(

                self.score_fvg(
                    fvg,
                    freshness_engine,
                    candles
                )

            )

        return sorted(

            ranked,

            key=lambda x:
                x["rank_score"],

            reverse=True

        )