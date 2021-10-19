from enum import Enum, auto

from survivor.utils.datetime import try_fromisoformat


class Game:
    def __init__(self):
        self.id = None
        self.week_id = None
        self.away_team_id = None
        self.home_team_id = None
        self.away_score = 0
        self.home_score = 0
        self.odds = None
        self.kickoff = None
        self.state = GameState.PREGAME

    @staticmethod
    def to_game(row, prefix=""):
        get_value = lambda key: row[f"{prefix}.{key}"] if prefix else row[key]

        game = Game()
        game.id = get_value("id")
        game.week_id = get_value("week_id")
        game.away_team_id = get_value("away_team_id")
        game.home_team_id = get_value("home_team_id")
        game.away_score = get_value("away_score")
        game.home_score = get_value("home_score")
        game.odds = get_value("odds")
        game.kickoff = try_fromisoformat(get_value("kickoff"))
        game.state = get_value("state")

        return game


class GameState(Enum):
    PREGAME = auto()
    IN_PROGRESS = auto()
    COMPLETE = auto()
