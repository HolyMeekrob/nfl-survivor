class Week:
    def __init__(self):
        self.id = None
        self.season_id = None
        self.number = None

    @staticmethod
    def to_week(row, prefix=""):
        get_value = lambda key: row[f"{prefix}.{key}"] if prefix else row[key]

        week = Week()
        week.id = get_value("id")
        week.season_id = get_value("season_id")
        week.number = get_value("number")

        return week
