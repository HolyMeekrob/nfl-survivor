from __future__ import annotations
from operator import neg

from survivor.data import User
from survivor.utils.list import indexes, map_list

from .pick_result import _PickResult as PickResult


class Score:
    user: User | None
    teams: list[str]
    misses: list[int]

    def __init__(self, results: list[PickResult]) -> None:
        if not results:
            self.user = None
            self.teams = []
            self.misses = []
        else:

            def get_week_number(pick: PickResult) -> int:
                return pick.week.number

            def get_team_name(pick: PickResult) -> str:
                return pick.team.abbreviation

            def get_is_correct(pick: PickResult) -> bool:
                return pick.is_correct

            sorted_results = sorted(results, key=get_week_number)
            self.user = sorted_results[0].user
            self.teams = map_list(get_team_name, sorted_results)
            self.misses = indexes(map_list(get_is_correct, sorted_results), False, 1)

    def __get_comparable(self: Score) -> tuple[int, list[int]]:
        return (len(self.misses), map_list(neg, self.misses))

    def __lt__(self, other: Score) -> bool:
        return self.__get_comparable() < other.__get_comparable()

    def __eq__(self, other: Score) -> bool:
        return self.__get_comparable() == other.__get_comparable()

    def week_str(self) -> str:
        return ", ".join([str(week + 1) for week in self.misses])

    def is_eliminated(self) -> bool:
        return len(self.misses) > 2
