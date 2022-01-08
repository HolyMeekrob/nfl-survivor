from datetime import datetime
from sqlite3 import Cursor
from typing import Callable

from survivor.data import Game, GameState, WeekTimer
from survivor.utils.datetime import utcnow
from survivor.utils.db import wrap_operation
from survivor.utils.list import groupby

from . import game as game_service, week as week_service


def is_sunday(kickoff: datetime):
    return kickoff.isoweekday() == 7


def get_first_game_kickoff(games: list[Game]) -> datetime:
    return sorted([game.kickoff for game in games])[0]


def get_first_sunday_kickoff(games: list[Game]) -> datetime:
    return sorted([game.kickoff for game in games if is_sunday(game.kickoff)])[0]


def get_first_batch_sunday_kickoff(games: list[Game]) -> datetime:
    groups = groupby(games, lambda game: game.kickoff)
    sunday_batches = sorted(
        [
            kickoff
            for kickoff in groups
            if is_sunday(kickoff) and len(groups[kickoff]) > 1
        ]
    )

    return sunday_batches[0] if sunday_batches else None


def get_last_game_kickoff(games: list[Game]) -> datetime:
    return sorted([game.kickoff for game in games], reverse=True)[0]


timer_deadlines: dict[WeekTimer, Callable[[list[Game]], datetime]] = {
    WeekTimer.FIRST_GAME: get_first_game_kickoff,
    WeekTimer.FIRST_GAME_SUNDAY: get_first_sunday_kickoff,
    WeekTimer.FIRST_BATCH_SUNDAY: get_first_batch_sunday_kickoff,
    WeekTimer.GAME_START: get_last_game_kickoff,
}


@wrap_operation()
def is_week_timer_active(week_id: int, week_timer: WeekTimer, *, cursor: Cursor = None):
    status = week_service.get_status_by_id(week_id, cursor=cursor)
    if status == GameState.COMPLETE:
        return False

    games = game_service.get_by_week(week_id, cursor=cursor)

    if not games:
        return False

    now = utcnow()
    deadline = timer_deadlines[week_timer](games)

    return deadline and deadline > now


@wrap_operation()
def get_deadline(week_id: int, week_timer: WeekTimer, *, cursor: Cursor):
    games = game_service.get_by_week(week_id, cursor=cursor)

    if not games:
        return None

    return timer_deadlines[week_timer](games)
