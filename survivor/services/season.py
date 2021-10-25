from operator import attrgetter

from survivor.api import get_season as fetch_season, get_week as fetch_week
from survivor.data import (
    GameState,
    InvitationStatus,
    Season,
    SeasonInvitation,
    SeasonType,
    User,
)
from survivor.utils.db import wrap_operation
from survivor.utils.list import flatten

from . import game as game_service
from . import week as week_service


@wrap_operation()
def get_all(*, cursor=None):
    cursor.execute("SELECT * FROM season;")
    seasons_raw = cursor.fetchall()

    return [Season.to_season(season) for season in seasons_raw]


@wrap_operation(is_write=True)
def create(year, *, cursor=None):
    cursor.execute(
        "INSERT INTO season (season_type, year) VALUES(:season_type, :year);",
        {"season_type": SeasonType.REGULAR.value, "year": year},
    )

    id = cursor.lastrowid

    weeks = fetch_season(year)

    for week in weeks:
        week_service.create(id, week, cursor=cursor)

    return id


@wrap_operation(is_write=True)
def update_games(id, *, cursor=None):
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
def get(id, *, cursor=None):
    cursor.execute("SELECT * FROM season WHERE id = :id LIMIT 1;", {"id": id})

    season_raw = cursor.fetchone()
    return Season.to_season(season_raw)


@wrap_operation()
def get_participants(id, *, cursor=None):
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
        {"season_id": id},
    )

    users_raw = cursor.fetchall()

    return [User.to_user(user) for user in users_raw]


@wrap_operation()
def get_status(id, *, cursor=None):
    weeks = week_service.get_by_season(id, cursor=cursor)
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
def get_invitations(id, *, cursor=None):
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
def create_invitation(id, user_id, *, cursor=None):
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
def is_season_joinable(season_id: int, *, cursor=None):
    status = get_status(season_id, cursor=cursor)
    return status == GameState.PREGAME
