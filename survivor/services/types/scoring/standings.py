from functools import reduce

from survivor.utils.list import append, count

from .score import Score

Standing = tuple[Score, int]


def get_standings(scores: list[Score]) -> list[Standing]:
    sorted_scores = sorted(scores)

    def add_place(places: list[Standing], score: Score) -> list[Standing]:
        if not places:
            return [(score, 1)]

        (prev_score, prev_place) = places[-1]
        prev_place_count = count(places, lambda pair: pair[1] == prev_place)

        next_place = (
            prev_place if prev_score == score else prev_place + prev_place_count
        )
        return append(places, (score, next_place))

    return reduce(add_place, sorted_scores, [])
