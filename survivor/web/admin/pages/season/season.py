from flask_wtf import FlaskForm
from wtforms.fields import HiddenField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email

from survivor.data.models.game import GameState
from survivor.data.models.season_invitation import InvitationStatus
from survivor.services.game import update


class SeasonViewModel:
    def __init__(
        self,
        season,
        weeks,
        status,
        participants,
        non_participants,
        update_games_form,
        invite_new_user_form,
    ):
        self.season = season
        self.weeks = weeks
        self.status = status
        self.participants = participants
        self.non_participants = non_participants
        self.update_games_form = update_games_form
        self.invite_new_user_form = invite_new_user_form

    def can_invite_users(self):
        return self.status == GameState.PREGAME

    def can_invite_user(self, non_participant):
        (_, invitations) = non_participant

        return InvitationStatus.PENDING not in invitations


class UpdateSeasonGamesForm(FlaskForm):
    id = HiddenField()


class InviteNewUserForm(FlaskForm):
    id = HiddenField()
    email = EmailField("New user", validators=[DataRequired(), Email()])
