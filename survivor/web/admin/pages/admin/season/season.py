from enum import Enum
from typing import Type

from flask_wtf import FlaskForm
from wtforms import (
    Field,
    Form,
    HiddenField,
    SelectField,
    ValidationError,
)
from wtforms.fields.html5 import DecimalField, EmailField, IntegerField
from wtforms.widgets import TextInput
from wtforms.validators import Email, InputRequired, NumberRange

from survivor.data import GameState, InvitationStatus, WeekTimer
from survivor.services.game import update


def get_enum_field(enum_type: Type[Enum], *args, **kwargs) -> SelectField:
    choices = [(elem.value, elem.name) for elem in list(enum_type)]
    coerce = lambda val: (val if isinstance(val, enum_type) else enum_type(int(val)))
    return SelectField(choices=choices, coerce=coerce, *args, **kwargs)


class FloatListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return ", ".join(map(str, self.data))
        else:
            return ""

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [float(val.strip()) for val in valuelist[0].split(",")]
        else:
            self.data = []


class SeasonViewModel:
    def __init__(
        self,
        season,
        weeks,
        status,
        participants,
        non_participants,
        update_games_form,
        update_rules_form,
        invite_new_user_form,
    ):
        self.season = season
        self.weeks = weeks
        self.status = status
        self.participants = participants
        self.non_participants = non_participants
        self.update_games_form = update_games_form
        self.update_rules_form = update_rules_form
        self.invite_new_user_form = invite_new_user_form

    def can_edit_rules(self):
        return True
        # return self.status == GameState.PREGAME

    def can_invite_users(self):
        return self.status == GameState.PREGAME

    def can_invite_user(self, non_participant):
        (_, invitations) = non_participant

        return InvitationStatus.PENDING not in invitations


class UpdateSeasonGamesForm(FlaskForm):
    id = HiddenField()


class UpdateRulesForm(FlaskForm):
    id = HiddenField()
    max_strikes = IntegerField(
        label="Max strikes",
        description="The maximum number of incorrect picks allowed in a season",
        default=1,
        validators=[InputRequired(), NumberRange(1)],
    )
    max_team_picks = IntegerField(
        label="Max picks per team",
        description="The maximum number of times the same team can be picked",
        default=1,
        validators=[InputRequired(), NumberRange(1)],
    )
    pick_cutoff = get_enum_field(
        WeekTimer,
        label="Pick cutoff",
        description="The deadline for when a user can change their pick. They can never change their pick to a game that has already begun.",
        default=WeekTimer.FIRST_GAME,
        validators=[InputRequired()],
    )
    pick_reveal = get_enum_field(
        WeekTimer,
        label="Pick reveal",
        description="The moment that the users' picks are revealed to the team. It is strongly recommended that this be no earlier than the pick cutoff.",
        default=WeekTimer.FIRST_GAME,
        validators=[InputRequired()],
    )
    entry_fee = DecimalField(
        label="Entry fee",
        description="The entry fee to enter the league",
        validators=[InputRequired(), NumberRange(0)],
    )
    winnings = FloatListField(
        label="Winnings allocation",
        description="The percentage of the entry fees that are awarded to each place, starting with first place. These values should add up to no more than 1.0.",
    )

    def validate_winnings(form: Form, field: Field):
        total = sum(field.data)

        if total != 1.0:
            raise ValidationError("Winnings must add up 1.0")


class InviteNewUserForm(FlaskForm):
    id = HiddenField()
    email = EmailField("New user", validators=[InputRequired(), Email()])
