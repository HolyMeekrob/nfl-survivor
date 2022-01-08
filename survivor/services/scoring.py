from sqlite3 import Cursor
from uuid import UUID

from survivor.data import Team, User, Week
from survivor.utils.db import wrap_operation
from survivor.utils.list import groupby, map_list


from .types.scoring.pick_result import (
    _PickResult as PickResult,
    _PickOutcome as PickOutcome,
)
from .rules import get as get_rules
from .types.scoring.score import Score
from .types.scoring.standings import get_standings as get_sorted_standings
from .week import get_by_season, get_current_week
from .week_timer import is_week_timer_active


@wrap_operation()
def get_standings(season_id: int, *, cursor: Cursor = None):
    weeks = get_by_season(season_id, cursor=cursor)

    if not weeks:
        return []

    completed_weeks = get_current_week(season_id, cursor=cursor).number - 1
    rules = get_rules(season_id, cursor=cursor)

    # Only show current week if the reveal timer is expired
    weeks = (
        weeks[:completed_weeks]
        if is_week_timer_active(weeks[completed_weeks].id, rules.pick_reveal)
        else weeks[: completed_weeks + 1]
    )

    weeks = [
        week
        for week in weeks
        if not is_week_timer_active(week.id, rules.pick_reveal, cursor=cursor)
    ]

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
                WHEN
                    game.state != 'COMPLETE'
                THEN
                    NULL
                WHEN
                    (game.home_score > game.away_score AND game.home_team_id = pick.team_id) OR (game.away_score > game.home_score AND game.away_team_id = pick.team_id)
                THEN
                    1
                ELSE
                    0
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
        """,
        {"season_id": season_id},
    )

    rows = cursor.fetchall()

    def to_game_outcome(is_correct: int | None) -> PickOutcome:
        if is_correct is None:
            return PickOutcome.NOT_YET_DECIDED
        return PickOutcome.CORRECT if is_correct == 1 else PickOutcome.INCORRECT

    picks = [
        PickResult(
            User.to_user(row, "user"),
            Team.to_team(row, "team"),
            Week.to_week(row, "week"),
            to_game_outcome(row["Is Correct"]),
        )
        for row in rows
    ]

    def get_user_id(pick: PickResult) -> UUID:
        return pick.user.id

    def get_score(user_picks: list[PickResult]) -> Score:
        return Score(user_picks, weeks, completed_weeks, rules.max_strikes)

    grouped_picks = list(groupby(picks, get_user_id).values())
    scores = map_list(get_score, grouped_picks)

    return get_sorted_standings(scores)
