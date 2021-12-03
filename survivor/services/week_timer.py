from datetime import datetime, timezone
from sqlite3 import Cursor
from typing import Callable

from survivor.data import Game, GameState, WeekTimer
from survivor.utils.db import wrap_operation
from survivor.utils.list import all, groupby

from . import game as game_service
from . import week as week_service


def none_have_started(games: list[Game]) -> bool:
    return all(games, lambda game: game.state == GameState.PREGAME)


def is_sunday(kickoff: datetime):
    return kickoff.isoweekday() == 7


def sunday_has_not_started(games: list[Game]) -> bool:
    earliest_sunday = sorted(
        [game.kickoff for game in games if is_sunday(game.kickoff)],
    )

    now = datetime.now(timezone.utc)

    return earliest_sunday and earliest_sunday[0] > now


def sunday_batch_has_not_started(games: list[Game]) -> bool:
    groups = groupby(games, lambda game: game.kickoff)
    sunday_batches = sorted(
        [
            kickoff
            for kickoff in groups
            if is_sunday(kickoff) and len(groups[kickoff]) > 1
        ]
    )

    now = datetime.now(timezone.utc)

    return sunday_batches and sunday_batches[0] > now


def any_have_not_started(games: list[Game]) -> bool:
    last_kickoff = sorted([game.kickoff for game in games], reverse=True)[0]

    now = datetime.now(timezone.utc)

    return last_kickoff > now


timer_policies: dict[WeekTimer, Callable[[list[Game]], bool]] = {
    WeekTimer.FIRST_GAME: none_have_started,
    WeekTimer.FIRST_GAME_SUNDAY: sunday_has_not_started,
    WeekTimer.FIRST_BATCH_SUNDAY: sunday_batch_has_not_started,
    WeekTimer.GAME_START: any_have_not_started,
}


@wrap_operation()
def is_week_timer_active(week_id: int, week_timer: WeekTimer, *, cursor: Cursor = None):
    status = week_service.get_status_by_id(week_id, cursor=cursor)
    if status == GameState.COMPLETE:
        return False

    week = week_service.get(week_id, cursor=cursor)

    if not week:
        return False

    games = game_service.get_by_week(week_id, cursor=cursor)
    return timer_policies[week_timer](games)
