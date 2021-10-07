class Season:
    def __init__(self):
        self.id = None
        self.season_type_id = None
        self.year = None

    @staticmethod
    def to_season(row, prefix=""):
        get_value = lambda key: row[f"{prefix}.{key}"] if prefix else row[key]

        season = Season()
        season.id = get_value("id")
        season.season_type_id = get_value("season_type")
        season.year = get_value("year")

        return season
