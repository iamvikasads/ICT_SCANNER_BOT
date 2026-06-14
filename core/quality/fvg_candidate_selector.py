class FVGCandidateSelector:

    def __init__(self):
        pass

    # ==================================
    # BEST FVG
    # ==================================

    def select_best(
        self,
        candidates
    ):

        if not candidates:
            return None

        return max(

            candidates,

            key=lambda x: x.get(
                "rank_score",
                0
            )

        )

    # ==================================
    # TOP N FVGS
    # ==================================

    def select_top(
        self,
        candidates,
        limit=3
    ):

        if not candidates:
            return []

        return sorted(

            candidates,

            key=lambda x: x.get(
                "rank_score",
                0
            ),

            reverse=True

        )[:limit]

    # ==================================
    # MIN SCORE FILTER
    # ==================================

    def filter_min_score(
        self,
        candidates,
        min_score=40
    ):

        if not candidates:
            return []

        return [

            candidate

            for candidate
            in candidates

            if candidate.get(
                "rank_score",
                0
            ) >= min_score

        ]

    # ==================================
    # FRESH ONLY
    # ==================================

    def filter_fresh(
        self,
        candidates,
        min_freshness=0.50
    ):

        if not candidates:
            return []

        return [

            candidate

            for candidate
            in candidates

            if candidate.get(
                "freshness_score",
                0
            ) >= min_freshness

        ]