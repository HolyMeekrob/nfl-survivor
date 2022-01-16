import uuid

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from survivor.data import Rules, User
from survivor.services import rules as rules_service
from survivor.services import season as season_service
from survivor.services import user as user_service
from survivor.services import week as week_service
from survivor.utils.datetime import utcnow
from survivor.utils.email import send_email
from survivor.utils.security import get_invitation_code

from .emails import SendInvitationEmailModel
from .pages import (
    InviteNewUserForm,
    SeasonViewModel,
    UpdateRulesForm,
    UpdateSeasonGamesForm,
)

admin = Blueprint("admin", __name__, url_prefix="/admin", template_folder=".")


@admin.get("/")
def index():
    return render_template("pages/admin/index.html")


@admin.get("/seasons")
def seasons():
    return render_template("pages/admin/seasons.html", seasons=season_service.get_all())


@admin.get("/season/<int:id>")
def season(
    id, *, update_games_form=None, update_rules_form=None, invite_new_user_form=None
):
    season = season_service.get(id)
    users = user_service.get_all()
    participants = season_service.get_participants(id)
    invitations = season_service.get_invitations(id)

    participant_ids = [participant.id for participant in participants]
    is_a_participant = lambda user: user.id in participant_ids
    get_invitations = lambda user: [
        invitation.status for invitation in invitations if invitation.user_id == user.id
    ]
    with_invitations = lambda user: (user, get_invitations(user))

    weeks = week_service.get_by_season(id)
    non_participants = [
        with_invitations(user) for user in users if not is_a_participant(user)
    ]
    status = season_service.get_status(id)

    update_games_form = update_games_form or UpdateSeasonGamesForm()
    update_games_form.id.data = id

    def get_rules_form():
        rules = rules_service.get(id)
        form = UpdateRulesForm()
        form.id.data = id
        form.max_strikes.data = rules.max_strikes
        form.max_team_picks.data = rules.max_team_picks
        form.pick_cutoff.data = rules.pick_cutoff
        form.pick_reveal.data = rules.pick_reveal
        form.entry_fee.data = rules.entry_fee
        form.winnings.data = rules.winnings

        return form

    update_rules_form = update_rules_form or get_rules_form()
    update_rules_form.id.data = id

    invite_new_user_form = invite_new_user_form or InviteNewUserForm()
    invite_new_user_form.id.data = id

    model = SeasonViewModel(
        season,
        weeks,
        status,
        participants,
        non_participants,
        update_games_form,
        update_rules_form,
        invite_new_user_form,
    )

    if not model:
        return abort(404)

    return render_template("pages/admin/season/season.html", model=model)


@admin.post("/season")
def create_season():
    year = utcnow().year

    try:
        id = season_service.create(year)

    except Exception:
        flash("Error creating season")
        return redirect(url_for("admin.seasons"))

    return redirect(url_for("admin.season", id=id))


@admin.post("/season/updateGames")
def update_games():
    form = UpdateSeasonGamesForm()
    id = int(form.id.data)

    if not form.validate_on_submit():
        return season(id, update_games_form=form)

    updated_games = season_service.update_games(id)

    if updated_games:
        flash("Games updated")
    else:
        flash("No games needed updating")

    return season(id, update_games_form=form)


@admin.post("/season/updateRules")
def update_rules():
    form = UpdateRulesForm()
    id = int(form.id.data)

    if form.validate():
        rules = Rules(
            id=id,
            max_strikes=form.max_strikes.data,
            max_team_picks=form.max_team_picks.data,
            pick_cutoff=form.pick_cutoff.data,
            pick_reveal=form.pick_reveal.data,
            entry_fee=float(form.entry_fee.data),
            winnings=form.winnings.data,
        )
        rules_service.upsert(rules)
        flash("Rules updated")

    return season(id, update_rules_form=form)


def __create_invitation(season_id, user_id, is_existing_user):
    if not user_id:
        return (False, "User does not exist")

    user = user_service.get(user_id)

    if not user:
        return (False, "User does not exist")

    invitation_id = season_service.create_invitation(season_id, user_id)

    if not invitation_id:
        return (False, "Error creating invitation")

    code = get_invitation_code(user.email)

    message = render_template(
        "emails/admin/invite/invite.html",
        model=SendInvitationEmailModel(
            current_user.name, current_app.config["APP_NAME"], is_existing_user, code
        ),
    )

    subject = "league invitation"

    result = send_email(user.email, subject, message)

    if not result:
        return (False, "Invitation created but there was an error sending the email")

    return (True, "")


@admin.post("/season/inviteUser")
def invite_user():
    data = request.get_json()
    season_id = data["seasonId"]
    user_id = uuid.UUID(data["userId"])

    result = __create_invitation(season_id, user_id, True)

    if not result[0]:
        flash(result[1])

    return season(season_id)


@admin.post("/season/inviteNewUser")
def invite_new_user():
    form = InviteNewUserForm()
    id = int(form.id.data)

    if not form.validate():
        return season(id, invite_new_user_form=form)

    email = form.email.data

    user = User.from_dictionary(
        {
            "email": email,
            "first_name": "",
            "last_name": "",
            "nickname": "",
            "password": "",
        }
    )
    user_id = user_service.create(user)
    result = __create_invitation(id, user_id, False)

    if not result[0]:
        flash(result[1])

    return season(id, invite_new_user_form=form)
