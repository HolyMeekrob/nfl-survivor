from sqlite3 import Cursor
from uuid import UUID

from survivor.data import GameState
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


@wrap_operation()
def is_season_joinable(season_id: int, *, cursor: Cursor = None):
    status = season_service.get_status(season_id, cursor=cursor)
    return status == GameState.PREGAME


@wrap_operation(is_write=True)
def join_season(season_id: int, user_id: UUID, *, cursor: Cursor = None):
    if is_already_participating(season_id, user_id, cursor=cursor):
        return False

    if not is_season_joinable:
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
