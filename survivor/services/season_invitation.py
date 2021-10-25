from sqlite3 import Cursor
from uuid import UUID

from survivor.data import InvitationStatus, Season
from survivor.services import season_participant as participant_service
from survivor.utils.db import wrap_operation


@wrap_operation()
def get_user_invitations(user_id: UUID, *, cursor: Cursor = None):
    cursor.execute(
        """
        SELECT
            season.*, season_invitation.status
        FROM
            user
        INNER JOIN
            season_invitation ON user.id = season_invitation.user_id
        INNER JOIN
            season ON season_invitation.season_id = season.id
        WHERE
            user.id = :user_id
        """,
        {"user_id": user_id},
    )

    raw_seasons = cursor.fetchall()

    return [(Season.to_season(season), season["status"]) for season in raw_seasons]


@wrap_operation(is_write=True)
def accept_invitations(season_id: int, user_id: UUID, *, cursor: Cursor = None):
    cursor.execute(
        """
        UPDATE
            season_invitation
        SET
            status = :accepted
        WHERE
            season_id = :season_id AND
            user_id = :user_id AND
            status = :pending
        """,
        {
            "season_id": season_id,
            "user_id": user_id,
            "accepted": InvitationStatus.ACCEPTED,
            "pending": InvitationStatus.PENDING,
        },
    )

    participant_service.join_season(season_id, user_id, cursor=cursor)

    return True


@wrap_operation(is_write=True)
def decline_invitations(season_id: int, user_id: UUID, *, cursor: Cursor = None):
    cursor.execute(
        """
        UPDATE
            season_invitation
        SET
            status = :declined
        WHERE
            season_id = :season_id AND
            user_id = :user_id AND
            status = :pending
        """,
        {
            "season_id": season_id,
            "user_id": user_id,
            "declined": InvitationStatus.DECLINED,
            "pending": InvitationStatus.PENDING,
        },
    )

    return True
