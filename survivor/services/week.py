from operator import attrgetter

from survivor.data import Week
from survivor.utils.db import wrap_operation
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
            season_id = :season_id;
        """,
        {"season_id": season_id},
    )

    weeks_raw = cursor.fetchall()

    return [Week.to_week(week) for week in weeks_raw]


@wrap_operation()
def get_status(week, *, cursor=None):
    games = game_service.get_by_week(week.id, cursor=cursor)
    return min(games, key=attrgetter("state.value")).state
