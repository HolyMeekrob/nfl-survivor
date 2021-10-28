class Team:
    id: int
    location: str
    name: str
    abbreviation: str

    def __init__(self):
        self.id = 0
        self.location = ""
        self.name = ""
        self.abbreviation = ""

    @staticmethod
    def to_team(row, prefix=""):
        get_value = lambda key: row[f"{prefix}.{key}"] if prefix else row[key]

        if not row:
            return None

        team = Team()
        team.id = get_value("id")
        team.location = get_value("location")
        team.name = get_value("name")
        team.abbreviation = get_value("abbreviation")

        return team
