from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import IntegerField, RadioField
from wtforms.widgets import HiddenInput
from wtforms.validators import InputRequired

from survivor.data import Game, GameState, Season, Week


class PickViewModel:
    def __init__(
        self,
        season: Season,
        week: Week,
        week_status: GameState,
        ineligible_teams: list[int],
        games: list[Game],
        form: PickForm,
    ):
        self.season = season
        self.week_status = week_status
        self.week = week
        self.can_enter_pick = week_status == GameState.PREGAME
        self.ineligible_teams = ineligible_teams
        self.games = games
        self.form = form


class PickForm(FlaskForm):
    team_id = RadioField(validators=[InputRequired()], coerce=int)
    season_id = IntegerField(widget=HiddenInput())
    week_id = IntegerField(widget=HiddenInput())
