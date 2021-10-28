from flask import Blueprint, abort, render_template
from flask_login import current_user
from typing import Callable
from uuid import UUID

from survivor.data import InvitationStatus
from survivor.services import (
    scoring as scoring_service,
    season as season_service,
    season_invitation as invitation_service,
)
from survivor.utils.functional import all_true
from .pages import MyInvitationsViewModel
from .pages import SeasonViewModel

home = Blueprint("home", __name__, template_folder=".")


@home.get("/")
def index():
    return render_template("pages/home/home.html")


@home.get("/invitations")
def get_my_invitations():
    invitations = invitation_service.get_user_invitations(current_user.id)
    model = MyInvitationsViewModel(invitations)

    return render_template("pages/home/invitations/invitations.html", model=model)


def __respond_to_invitation(service_call: Callable[[int, UUID], bool], season_id: int):
    user_id = current_user.id
    invitations = invitation_service.get_user_invitations(user_id)

    for_season = lambda invitation: invitation[0].id == season_id
    is_pending = lambda invitation: invitation[1] == InvitationStatus.PENDING

    can_be_accepted = all_true(for_season, is_pending)
    active_invitations = list(filter(can_be_accepted, invitations))

    if not active_invitations:
        abort(401, "You do not have a pending invitation to the given season")

    service_call(season_id, user_id)

    return get_my_invitations()


@home.post("/acceptInvitation/<int:season_id>")
def accept_invitation(season_id: int):
    return __respond_to_invitation(invitation_service.accept_invitations, season_id)


@home.post("/declineInvitation/<int:season_id>")
def decline_invitation(season_id: int):
    return __respond_to_invitation(invitation_service.decline_invitations, season_id)


@home.get("/season/<int:season_id>")
def season(season_id: int):
    season = season_service.get(season_id)
    standings = scoring_service.get_standings(season_id)
    model = SeasonViewModel(season, standings)

    return render_template("pages/home/season/season.html", model=model)
