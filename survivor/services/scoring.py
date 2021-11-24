from sqlite3 import Cursor
from uuid import UUID

from survivor.data import Team, User, Week
from survivor.utils.db import wrap_operation
from survivor.utils.list import groupby, map_list


from .types.scoring.pick_result import _PickResult as PickResult
from .types.scoring.score import Score
from .types.scoring.standings import get_standings as get_sorted_standings
from .week import get_completed_weeks

# TODO: This needs to come from the season (probably need a new rules object)
def __get_max_strikes():
    return 3


@wrap_operation()
def get_standings(season_id: int, *, cursor: Cursor = None):
    completed_weeks = get_completed_weeks(season_id, cursor=cursor)

    if not completed_weeks:
        return []

    last_week_number = completed_weeks[-1].number

    def prepend(prefix):
        return lambda s: f"{prefix}{s} AS '{prefix}{s}'"

    user_keys = ", ".join(map(prepend("user."), vars(User()).keys()))
    team_keys = ", ".join(map(prepend("team."), vars(Team()).keys()))
    week_keys = ", ".join(map(prepend("week."), vars(Week()).keys()))

    cursor.execute(
        f"""
        SELECT
            {user_keys},
            {team_keys},
            {week_keys},
            CASE
                WHEN (game.home_score > game.away_score AND game.home_team_id = pick.team_id) OR (game.away_score > game.home_score AND game.away_team_id = pick.team_id)
                THEN 1
                ELSE 0
            END as 'Is Correct'
        FROM
            pick
        INNER JOIN
            week ON pick.week_id = week.id
        INNER JOIN
            user ON pick.user_id = user.id
        INNER JOIN
            team ON pick.team_id = team.id
        INNER JOIN
            game ON (pick.team_id = game.away_team_id OR pick.team_id = game.home_team_id) AND game.week_id = week.id
        WHERE
            week.season_id = :season_id
            AND week.number <= :last_week_number
        """,
        {"season_id": season_id, "last_week_number": last_week_number},
    )

    rows = cursor.fetchall()

    picks = [
        PickResult(
            User.to_user(row, "user"),
            Team.to_team(row, "team"),
            Week.to_week(row, "week"),
            bool(row["Is Correct"]),
        )
        for row in rows
    ]

    def get_user_id(pick: PickResult) -> UUID:
        return pick.user.id

    def get_score(user_picks: list[PickResult]) -> Score:
        return Score(user_picks, completed_weeks, __get_max_strikes())

    grouped_picks = list(groupby(picks, get_user_id).values())
    scores = map_list(get_score, grouped_picks)

    return get_sorted_standings(scores)
