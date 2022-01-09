from operator import attrgetter
from sqlite3 import Cursor
from typing import Callable

from survivor.api import get_season as fetch_season
from survivor.api import get_week as fetch_week
from survivor.data import (
    GameState,
    InvitationStatus,
    Rules,
    Season,
    SeasonInvitation,
    SeasonType,
    User,
)
from survivor.services.types.scoring.standings import Standing
from survivor.utils.db import wrap_operation
from survivor.utils.functional import complement
from survivor.utils.list import first, flatten

from . import game as game_service
from . import rules as rules_service
from . import scoring as scoring_service
from . import week as week_service


@wrap_operation()
def get_all(*, cursor: Cursor = None):
    cursor.execute("SELECT * FROM season ORDER BY year;")
    seasons_raw = cursor.fetchall()

    return [Season.to_season(season) for season in seasons_raw]


@wrap_operation()
def get_by_year(year: int, *, cursor: Cursor = None):
    cursor.execute("SELECT * FROM season WHERE year = :year;", {"year": year})
    seasons_raw = cursor.fetchall()

    return [Season.to_season(season) for season in seasons_raw]


@wrap_operation(is_write=True)
def create(year, *, cursor: Cursor = None):
    cursor.execute(
        "INSERT INTO season (season_type, year) VALUES(:season_type, :year);",
        {"season_type": SeasonType.REGULAR.value, "year": year},
    )

    id = cursor.lastrowid

    rules_service.upsert(Rules(id=id), cursor=Cursor)

    weeks = fetch_season(year)

    for week in weeks:
        week_service.create(id, week, cursor=cursor)

    return id


@wrap_operation(is_write=True)
def update_games(id, *, cursor: Cursor = None):
    def update_completed_weeks(year, weeks):
        if not weeks:
            return []

        week = weeks[0]

        if week_service.get_status(week, cursor=cursor) == GameState.COMPLETE:
            return update_completed_weeks(year, weeks[1:])

        week = fetch_week(year, week.number)
        games = [
            game_service.update_from_api(year, week.number, game, cursor=cursor)
            for game in week.games
        ]

        status = min(flatten(games), key=attrgetter("state.value")).state

        # If this week is complete, update the next week
        # Otherwise the next week hasn't started yet and so we can stop recursing
        return (
            games + update_completed_weeks(year, weeks[1:])
            if status == GameState.COMPLETE
            else []
        )

    season = get(id, cursor=cursor)

    weeks = week_service.get_by_season(id, cursor=cursor) or []
    weeks.sort(key=attrgetter("number"))

    return update_completed_weeks(season.year, weeks)


@wrap_operation()
def get(season_id: int, *, cursor: Cursor = None) -> Season:
    cursor.execute("SELECT * FROM season WHERE id = :id LIMIT 1;", {"id": season_id})

    season_raw = cursor.fetchone()
    return Season.to_season(season_raw)


@wrap_operation()
def get_participants(season_id: int, *, cursor: Cursor = None):
    cursor.execute(
        """
        SELECT
            user.*
        FROM
            user
        INNER JOIN
            season_participant sp ON user.id = sp.user_id
        WHERE
            sp.season_id = :season_id;
        """,
        {"season_id": season_id},
    )

    users_raw = cursor.fetchall()

    return [User.to_user(user) for user in users_raw]


@wrap_operation()
def get_status(season_id: int, *, cursor: Cursor = None):
    weeks = week_service.get_by_season(season_id, cursor=cursor)
    statuses = [week_service.get_status(week, cursor=cursor) for week in weeks]

    all_have_status = lambda status: all(
        [week_status == status for week_status in statuses]
    )

    if all_have_status(GameState.PREGAME):
        return GameState.PREGAME

    if all_have_status(GameState.COMPLETE):
        return GameState.COMPLETE

    return GameState.IN_PROGRESS


@wrap_operation()
def is_complete(season_id: int, *, cursor: Cursor = None):
    return get_status(season_id, cursor=cursor) == GameState.COMPLETE


is_incomplete: Callable[[int], bool] = complement(is_complete)


@wrap_operation()
def get_invitations(id, *, cursor: Cursor = None):
    cursor.execute(
        "SELECT * FROM season_invitation WHERE season_id = :season_id;",
        {"season_id": id},
    )

    raw_invitations = cursor.fetchall()

    return [
        SeasonInvitation.to_season_invitation(invitation)
        for invitation in raw_invitations
    ]


@wrap_operation(is_write=True)
def create_invitation(id, user_id, *, cursor: Cursor = None):
    cursor.execute(
        """
        INSERT INTO
            season_invitation
                (season_id, user_id, status)
            VALUES
                (:season_id, :user_id, :status);
        """,
        {"season_id": id, "user_id": user_id, "status": InvitationStatus.PENDING},
    )

    return cursor.lastrowid


@wrap_operation()
def is_season_joinable(season_id: int, *, cursor: Cursor = None):
    status = get_status(season_id, cursor=cursor)
    return status == GameState.PREGAME


@wrap_operation()
def get_current_seasons(*, cursor=None):
    seasons = get_all(cursor=cursor)
    # Do not use first() since that will run the
    # (slow) predicate function for all seasons
    for season in seasons:
        if get_status(season.id, cursor=cursor) != GameState.COMPLETE:
            return [s for s in seasons if s.year == season.year]


@wrap_operation()
def get_champions(season_id: int, *, cursor: Cursor = None):
    def is_first_place(standing: Standing):
        return standing[1] == 1

    is_not_first_place = complement(is_first_place)

    def has_single_player_in_first_place(standings: list[Standing]):
        return len(filter(is_first_place), standings) == 1

    def has_fewer_remaining_weeks_than_miss_gap(standings: list[Standing]):
        miss_gap = len(first(standings, is_not_first_place)[0].misses) - len(
            standings[0][0].misses
        )
        incomplete_week_count = len(
            week_service.get_incomplete_weeks(season_id, cursor=cursor)
        )

        return incomplete_week_count < miss_gap

    def is_champion_decided(standings: list[Standing]):
        return has_single_player_in_first_place(
            standings
        ) and has_fewer_remaining_weeks_than_miss_gap(standings)

    standings = scoring_service.get_standings(season_id, cursor=cursor)

    if is_complete(season_id) or is_champion_decided(standings):
        return [standing[0].user.id for standing in standings if standing[1] == 1]

    return None
