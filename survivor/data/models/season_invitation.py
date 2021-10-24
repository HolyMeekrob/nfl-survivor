from enum import Enum, auto


class SeasonInvitation:
    def __init__(self):
        self.season_id = None
        self.user_id = None
        self.status = InvitationStatus.PENDING

    @staticmethod
    def to_season_invitation(row, prefix=""):
        get_value = lambda key: row[f"{prefix}.{key}"] if prefix else row[key]

        season_invitation = SeasonInvitation()
        season_invitation.season_id = get_value("season_id")
        season_invitation.user_id = get_value("user_id")
        season_invitation.status = get_value("status")

        return season_invitation


class InvitationStatus(Enum):
    PENDING = auto()
    ACCEPTED = auto()
    DECLINED = auto()
    REVOKED = auto()
    EXPIRED = auto()
    CANCELED = auto()
