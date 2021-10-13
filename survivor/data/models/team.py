class Team:
    def __init__(self):
        self.id = None
        self.location = None
        self.name = None
        self.abbreviation = None

    @staticmethod
    def to_team(row):
        team = Team()
        team.id = row["id"]
        team.location = row["location"]
        team.name = row["name"]
        team.abbreviation = row["abbreviation"]

        return team
