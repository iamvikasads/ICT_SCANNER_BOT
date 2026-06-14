class CandidateSelector:

    def __init__(self):
        pass

    # ==================================
    # BEST CANDIDATE
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
    # TOP N CANDIDATES
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
        min_score
    ):

        if not candidates:
            return []

        return [

            candidate

            for candidate in candidates

            if candidate.get(
                "rank_score",
                0
            ) >= min_score

        ]