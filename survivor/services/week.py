from itertools import dropwhile, takewhile
from operator import attrgetter
from sqlite3 import Cursor

from survivor.data import GameState, Week
from survivor.utils.db import wrap_operation
from survivor.utils.list import first
from . import game as game_service


@wrap_operation()
def __is_complete(week: Week, *, cursor: Cursor = None):
    return get_status(week, cursor=cursor) == GameState.COMPLETE


@wrap_operation(is_write=True)
def create(season_id: int, week: Week, *, cursor: Cursor = None) -> int:
    cursor.execute(
        "INSERT INTO week (season_id, number) VALUES(:season_id, :number);",
        {"season_id": season_id, "number": week.number},
    )

    id = cursor.lastrowid

    for game in week.games:
        game_service.create(id, game, cursor=cursor)

    return id


@wrap_operation()
def get(week_id: int, *, cursor: Cursor = None):
    cursor.execute("SELECT * FROM week WHERE id = :id", {"id": week_id})

    week_raw = cursor.fetchone()
    return Week.to_week(week_raw)


@wrap_operation()
def get_by_season(season_id: int, *, cursor: Cursor = None) -> list[Week]:
    cursor.execute(
        """
        SELECT
            *
        FROM
            week
        WHERE
            season_id = :season_id
        ORDER BY
            number;
        """,
        {"season_id": season_id},
    )

    weeks_raw = cursor.fetchall()

    return [Week.to_week(week) for week in weeks_raw]


@wrap_operation()
def get_current_week(season_id: int, *, cursor: Cursor = None):
    weeks = get_by_season(season_id, cursor=cursor)

    def is_incomplete(week: Week):
        return not __is_complete(week, cursor=cursor)

    return first(weeks, is_incomplete)


@wrap_operation()
def get_completed_weeks(season_id, *, cursor: Cursor = None):
    weeks = get_by_season(season_id, cursor=cursor)

    return list(takewhile(__is_complete, weeks))


@wrap_operation()
def get_incomplete_weeks(season_id: int, *, cursor: Cursor = None):
    weeks = get_by_season(season_id, cursor=cursor)

    return list(dropwhile(__is_complete, weeks))


@wrap_operation()
def get_status_by_id(week_id: int, *, cursor: Cursor = None):
    games = game_service.get_by_week(week_id, cursor=cursor)
    return min(games, key=attrgetter("state.value")).state


@wrap_operation()
def get_status(week: Week, *, cursor: Cursor = None):
    return get_status_by_id(week.id, cursor=cursor)
