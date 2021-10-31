from sqlite3 import Cursor
from uuid import UUID

from survivor.data import Season
from survivor.services import season as season_service
from survivor.utils.db import wrap_operation


@wrap_operation()
def is_already_participating(season_id: int, user_id: UUID, *, cursor: Cursor = None):
    cursor.execute(
        """
        SELECT
            *
        FROM
            season_participant
        WHERE
            season_id = :season_id AND
            user_id = :user_id
        """,
        {"season_id": season_id, "user_id": user_id},
    )

    return bool(cursor.fetchall())


@wrap_operation(is_write=True)
def join_season(season_id: int, user_id: UUID, *, cursor: Cursor = None):
    if is_already_participating(season_id, user_id, cursor=cursor):
        return False

    if not season_service.is_season_joinable(season_id, cursor=cursor):
        return False

    cursor.execute(
        """
        INSERT INTO
            season_participant
                (season_id, user_id)
            VALUES
                (:season_id, :user_id)
        """,
        {"season_id": season_id, "user_id": user_id},
    )

    return cursor.lastrowid


@wrap_operation()
def get_seasons_for_user(user_id: UUID, *, cursor: Cursor = None) -> list[Season]:
    cursor.execute(
        """
        SELECT
            season.*
        FROM
            season_participant sp
        INNER JOIN
            season on sp.season_id = season.id
        WHERE
            sp.user_id = :user_id
        """,
        {"user_id": user_id},
    )

    raw_seasons = cursor.fetchall()

    return [Season.to_season(season) for season in raw_seasons]
