class OBRanker:

    def __init__(self):
        pass

    # ==================================
    # SCORE SINGLE OB
    # ==================================

    def score(
        self,
        ob,
        fresh=True
    ):

        if ob is None:
            return None

        score = 0

        # ==========================
        # MSS CAUSING OB
        # ==========================

        score += 3

        # ==========================
        # HAS FVG
        # ==========================

        if ob.get(
            "has_fvg",
            False
        ):

            score += 2

        # ==========================
        # DISTANCE TO MSS
        # ==========================

        distance = (
            ob.get(
                "distance_to_mss",
                999
            )
        )

        if distance <= 3:

            score += 2

        elif distance <= 6:

            score += 1

        # ==========================
        # DISPLACEMENT
        # ==========================

        displacement = (
            ob.get(
                "displacement_ratio",
                1
            )
        )

        if displacement >= 3:

            score += 2

        elif displacement >= 2:

            score += 1

        # ==========================
        # FRESHNESS BONUS
        # ==========================

        if fresh:

            score += 1

        ranked_ob = dict(ob)

        ranked_ob[
            "rank_score"
        ] = score

        return ranked_ob

    # ==================================
    # SCORE ALL OBS
    # ==================================

    def score_all(
        self,
        obs,
        freshness_engine=None,
        candles=None
    ):

        ranked = []

        for ob in obs:

            fresh = True

            if (

                freshness_engine
                is not None

                and

                candles is not None

            ):

                fresh = (
                    freshness_engine
                    .is_ob_fresh(
                        candles,
                        ob
                    )
                )

            if not fresh:
                continue

            result = (
                self.score(
                    ob,
                    fresh=True
                )
            )

            if result:

                ranked.append(
                    result
                )

        return ranked