class Week:
    def __init__(self, number, games):
        has_teams = lambda game: game.away_team != None and game.home_team != None

        self.number = number
        self.games = [game for game in games if has_teams(game)]

    def __str__(self):
        games = "\n".join(list(map(str, self.games)))
        return f"Week {self.number}\n{games}"
