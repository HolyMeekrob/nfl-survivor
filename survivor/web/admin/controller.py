from datetime import datetime
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

from survivor.data import User
from survivor.services import (
    season as season_service,
    week as week_service,
    user as user_service,
)
from survivor.utils.email import send_email
from survivor.utils.security import get_invitation_code

from .emails import SendInvitationEmailModel
from .pages import InviteNewUserForm, SeasonViewModel, UpdateSeasonGamesForm

admin = Blueprint("admin", __name__, url_prefix="/admin", template_folder=".")


@admin.get("/")
def index():
    return render_template("pages/admin/index.html")


@admin.get("/seasons")
def seasons():
    return render_template("pages/admin/seasons.html", seasons=season_service.get_all())


@admin.get("/season/<int:id>")
def season(id, *, update_games_form=None, invite_new_user_form=None):
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

    invite_new_user_form = invite_new_user_form or InviteNewUserForm()
    invite_new_user_form.id.data = id

    model = SeasonViewModel(
        season,
        weeks,
        status,
        participants,
        non_participants,
        update_games_form,
        invite_new_user_form,
    )

    if not model:
        return abort(404)

    return render_template("pages/admin/season/season.html", model=model)


@admin.post("/season")
def create_season():
    year = datetime.utcnow().year

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

    if not form.validate():
        return season(id, update_games_form=form)

    updated_games = season_service.update_games(id)

    if updated_games:
        flash("Games updated")
    else:
        flash("No games needed updating")

    return season(id, update_games_form=form)


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
