from enum import Enum, auto


class Game:
    def __init__(self):
        self.date = None
        self.away_team = None
        self.home_team = None
        self.away_score = None
        self.home_score = None
        self.odds = None
        self.state = None

    def __str__(self):
        if self.away_score != None and self.home_score != None:
            return f"{self.away_team} ({self.away_score}) at {self.home_team} ({self.home_score})"

        return f"{self.away_team} at {self.home_team} ({str(self.date)}) ({self.odds})"

    def add_team(self, team):
        if self.away_team == None:
            self.away_team = team
        elif self.home_team == None:
            self.home_team = team
        else:
            raise

    def add_score(self, score):
        if self.away_score == None:
            self.away_score = score
        elif self.home_score == None:
            self.home_score = score
        else:
            raise


class GameState(Enum):
    PREGAME = auto()
    IN_PROGRESS = auto()
    COMPLETE = auto()
