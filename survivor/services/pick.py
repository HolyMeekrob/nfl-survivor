from sqlite3 import Cursor
from uuid import UUID

from survivor.utils.db import wrap_operation


@wrap_operation()
def get_pick(user_id: UUID, week_id: int, *, cursor: Cursor = None) -> int | None:
    cursor.execute(
        """
        SELECT
            team_id
        FROM
            pick
        WHERE
            user_id = :user_id AND
            week_id = :week_id
        """,
        {"user_id": user_id, "week_id": week_id},
    )

    row = cursor.fetchone()

    return row["team_id"] if row else None


@wrap_operation()
def get_picked_teams(
    user_id: UUID, season_id: int, *, cursor: Cursor = None
) -> list[tuple[int, int]]:
    cursor.execute(
        """
        SELECT
            pick.team_id,
            week.number
        FROM
            pick
            INNER JOIN week ON pick.week_id = week.id
            
        WHERE
            pick.user_id = :user_id AND
            week.season_id = :season_id
        ORDER BY
            week.number
        """,
        {"user_id": user_id, "season_id": season_id},
    )

    rows = cursor.fetchall()

    return [(row["number"], row["team_id"]) for row in rows]


@wrap_operation(is_write=True)
def make_pick(user_id: UUID, week_id: int, team_id: int, *, cursor: Cursor = None):
    cursor.execute(
        """
        INSERT INTO
            pick
                (week_id, user_id, team_id)
            VALUES
                (:week_id, :user_id, :team_id)
            ON
                CONFLICT(week_id, user_id)
                DO UPDATE
                    SET team_id = :team_id;
        """,
        {"user_id": user_id, "week_id": week_id, "team_id": team_id},
    )

    return cursor.lastrowid
