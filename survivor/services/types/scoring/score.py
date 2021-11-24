from __future__ import annotations
from functools import reduce
from operator import neg

from survivor.data import User, Week
from survivor.utils.list import append, indexes, map_list

from .pick_result import _PickResult as PickResult


class Score:
    user: User | None
    teams: list[str]
    misses: list[int]
    max_strikes: int

    def __init__(
        self, results: list[PickResult], weeks: list[Week], max_strikes: int
    ) -> None:
        self.max_strikes = max_strikes

        if not results:
            self.user = None
            self.teams = []
            self.misses = []
        else:

            def get_user() -> User:
                return results[0].user

            def get_week_number(pick: PickResult) -> int:
                return pick.week.number

            def get_team_name(pick: PickResult) -> str:
                return "N/A" if pick.team is None else pick.team.abbreviation

            def get_is_correct(pick: PickResult) -> bool:
                return pick.is_correct

            def get_empty_pick(week) -> PickResult:
                return PickResult(get_user(), None, week, False)

            def fill_gaps(picks: list[PickResult]) -> list[PickResult]:
                def fill(
                    aggregate: tuple[list[PickResult], list[PickResult], int],
                    week: Week,
                ) -> tuple[list[PickResult], list[PickResult], int]:
                    (remaining_picks, all_picks, remaining_strikes) = aggregate

                    if remaining_strikes == 0:
                        return aggregate

                    # If there are no more picks to choose from,
                    # or the next pick doesn't match the next week
                    # append an empty pick
                    if (
                        not remaining_picks
                        or remaining_picks[0].week.number != week.number
                    ):
                        return (
                            remaining_picks,
                            append(all_picks, get_empty_pick(week)),
                            remaining_strikes - 1,
                        )

                    updated_strikes = (
                        remaining_strikes
                        if remaining_picks[0].is_correct
                        else remaining_strikes - 1
                    )

                    return (
                        remaining_picks[1:],
                        append(all_picks, remaining_picks[0]),
                        updated_strikes,
                    )

                return reduce(fill, weeks, (picks, [], max_strikes))[1]

            sorted_results = fill_gaps(sorted(results, key=get_week_number))

            self.user = get_user()
            self.teams = map_list(get_team_name, sorted_results)
            self.misses = indexes(map_list(get_is_correct, sorted_results), False, 1)

    def __get_comparable(self: Score) -> tuple[int, list[int]]:
        below_max_strikes = len(self.misses) < self.max_strikes
        sortable_misses = map_list(neg, self.misses)
        return (
            (0, len(self.misses), sortable_misses)
            if below_max_strikes
            else (1, neg(len(self.teams)), sortable_misses)
        )

    def __lt__(self, other: Score) -> bool:
        return self.__get_comparable() < other.__get_comparable()

    def __eq__(self, other: Score) -> bool:
        return self.__get_comparable() == other.__get_comparable()

    def week_str(self) -> str:
        return ", ".join([str(week + 1) for week in self.misses])

    def is_eliminated(self) -> bool:
        return len(self.misses) > 2
