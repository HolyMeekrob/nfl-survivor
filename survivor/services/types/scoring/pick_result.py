from survivor.data import Team, User, Week


class _PickResult:
    def __init__(self, user: User, team: Team, week: Week, is_correct: bool) -> None:
        self.user = user
        self.team = team
        self.week = week
        self.is_correct = is_correct
