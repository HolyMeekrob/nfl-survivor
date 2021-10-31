from operator import attrgetter
from sqlite3 import Cursor

from survivor.data import Week
from survivor.data.models.game import GameState
from survivor.utils.db import wrap_operation
from survivor.utils.list import first
from . import game as game_service


@wrap_operation(is_write=True)
def create(season_id, week, *, cursor=None):
    cursor.execute(
        "INSERT INTO week (season_id, number) VALUES(:season_id, :number);",
        {"season_id": season_id, "number": week.number},
    )

    id = cursor.lastrowid

    for game in week.games:
        game_service.create(id, game, cursor=cursor)

    return id


@wrap_operation()
def get_by_season(season_id, *, cursor=None):
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
def get_current_week(season_id, *, cursor: Cursor = None):
    weeks = get_by_season(season_id, cursor=cursor)

    def is_incomplete(week: Week):
        return get_status(week, cursor=cursor) != GameState.COMPLETE

    return first(weeks, is_incomplete)


@wrap_operation()
def get_status_by_id(week_id: int, *, cursor: Cursor = None):
    games = game_service.get_by_week(week_id, cursor=cursor)
    return min(games, key=attrgetter("state.value")).state


@wrap_operation()
def get_status(week: Week, *, cursor: Cursor = None):
    return get_status_by_id(week.id)
