from sqlite3 import Cursor
from typing import Callable
from uuid import UUID

from survivor.data import Game, GameState, Pick, User, WeekTimer
from survivor.utils.db import wrap_operation
from survivor.utils.list import first

from . import game as game_service
from . import week_timer as week_timer_service


@wrap_operation()
def get_pick(user_id: UUID, week_id: int, *, cursor: Cursor = None):
    cursor.execute(
        """
        SELECT
            *
        FROM
            pick
        WHERE
            user_id = :user_id AND
            week_id = :week_id;
        """,
        {"user_id": user_id, "week_id": week_id},
    )

    row = cursor.fetchone()

    return Pick.to_pick(row)


@wrap_operation()
def get_picks_for_week(week_id: int, *, cursor: Cursor = None):
    cursor.execute(
        """
        SELECT
            *
        FROM
            pick
        WHERE
            week_id = :week_id;
        """,
        {"week_id": week_id},
    )

    rows = cursor.fetchall()

    return [Pick.to_pick(row) for row in rows]


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


@wrap_operation()
def get_game(pick: Pick, *, cursor: Cursor = None):
    def has_team(team_id: int) -> Callable[[Game], bool]:
        return lambda game: game.home_team_id == team_id or game.away_team_id == team_id

    games = game_service.get_by_week(pick.week_id, cursor=cursor)

    return first(games, has_team(pick.team_id))


@wrap_operation()
def can_enter_pick(
    week_timer: WeekTimer, week_id: int, user: User, *, cursor: Cursor = None
) -> bool:
    def has_picked_game_not_yet_started():
        current_pick = get_pick(user.id, week_id)

        if not current_pick:
            return True

        game = get_game(current_pick, cursor=cursor)
        return (not game) or game.state == GameState.PREGAME

    def is_week_timer_active():
        return week_timer_service.is_week_timer_active(
            week_id, week_timer, cursor=cursor
        )

    return has_picked_game_not_yet_started() and is_week_timer_active()
