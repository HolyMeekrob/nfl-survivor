from flask import Blueprint, Flask, abort, current_app, flash, render_template
from flask_login import current_user
from typing import Callable
from uuid import UUID

from survivor.data import GameState, InvitationStatus, Season, Team
from survivor.services import (
    game as game_service,
    pick as pick_service,
    rules as rules_service,
    scoring as scoring_service,
    season as season_service,
    season_invitation as invitation_service,
    season_participant as participant_service,
    team as team_service,
    week as week_service,
)
from survivor.utils.functional import all_true, always, identity
from survivor.utils.list import filter_list, first, groupby
from survivor.web.home.pages.home.pick.pick import PickViewModel

from .pages import MyInvitationsViewModel
from .pages import PickForm, PickViewModel
from .pages import SeasonViewModel

home = Blueprint("home", __name__, template_folder=".")


# TODO: This should come from db or config
def __get_pick_message(app: Flask, team: Team):
    default_msg = f"You have selected the {team.location} {team.name}. Good luck!"
    return app.config["CUSTOM_PICK_MESSAGES"].get(team.abbreviation, default_msg)


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
        abort(403, "You do not have a pending invitation to the given season")

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
    seasons = participant_service.get_seasons_for_user(current_user.id)

    is_user_in_season = any(seasons, lambda s: s.id == season_id)

    # TODO: Allow admins
    if not is_user_in_season:
        abort(403, "You are not a participant in this season")

    season = season_service.get(season_id)
    standings = scoring_service.get_standings(season_id)
    model = SeasonViewModel(season, standings)

    return render_template("pages/home/season/season.html", model=model)


def pick(form: PickForm = None):
    user_id = current_user.id
    seasons = participant_service.get_seasons_for_user(user_id)

    def is_incomplete(season: Season) -> bool:
        return season_service.is_incomplete(season.id)

    active_seasons = filter_list(is_incomplete, seasons)

    # TODO: Do we need to support multiple seasons?
    active_season = first(active_seasons, always(True))
    active_week = (
        week_service.get_current_week(active_season.id) if active_season else None
    )
    rules = rules_service.get(active_season.id)

    picks = (
        pick_service.get_picked_teams(user_id, active_season.id)
        if active_season
        else []
    )

    pick = first(picks, lambda p: p[0] == active_week.number)
    picked_team = pick[1] if pick else None

    previously_picked_teams = [p[1] for p in picks if p[0] != active_week.number]
    pick_counts = groupby(previously_picked_teams, identity)
    ineligible_teams = [
        team_id
        for team_id in pick_counts
        if len(pick_counts[team_id]) >= rules.max_team_picks
    ]

    games = game_service.get_by_week(active_week.id) if active_week else None

    if not form:
        form = PickForm()
        form.team_id.choices = [
            (team.id, team.abbreviation) for team in team_service.get_all()
        ]
        form.team_id.data = picked_team
        form.season_id.data = active_season.id if active_season else None
        form.week_id.data = active_week.id if active_week else None

    can_enter_pick = pick_service.can_enter_pick(
        rules.pick_cutoff, active_week.id, current_user
    )

    model = PickViewModel(
        active_season, active_week, can_enter_pick, ineligible_teams, games, form
    )

    return render_template("pages/home/pick/pick.html", model=model)


@home.get("/pick")
def get_pick():
    return pick()


@home.post("/pick")
def post_pick():
    form = PickForm()

    all_teams = team_service.get_all()
    form.team_id.choices = [(team.id, team.abbreviation) for team in all_teams]

    def handle_error(msg: str | None = None):
        if msg:
            flash(msg)
        return pick(form)

    if not form.validate():
        return handle_error()

    user_id = current_user.id
    picked_team = form.team_id.data
    season_id = form.season_id.data
    week_id = form.week_id.data

    previously_picked_ids = pick_service.get_picked_teams(user_id, season_id)
    if picked_team in previously_picked_ids:
        return handle_error(
            "Cannot pick a team that has already been picked this season"
        )

    if season_service.is_complete(season_id):
        return handle_error("Season has already completed")

    current_week = week_service.get_current_week(season_id)

    if not current_week or current_week.id != week_id:
        return handle_error("Picks can only be entered for the current week")

    if week_service.get_status_by_id(week_id) != GameState.PREGAME:
        return handle_error("Week has already started; picks can no longer be entered")

    pick_service.make_pick(user_id, week_id, picked_team)

    pick_msg = __get_pick_message(
        current_app, first(all_teams, lambda team: team.id == picked_team)
    )
    flash(pick_msg)
    return pick(form)
