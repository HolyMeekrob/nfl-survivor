from survivor.data import Season
from survivor.services.types import Standing


class SeasonViewModel:
    season: Season
    standings: list[Standing]

    def __init__(self, season: Season, standings: list[Standing]) -> None:
        self.season = season
        self.standings = standings
