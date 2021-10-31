from __future__ import annotations
from sqlite3 import Row


class Season:
    id: int
    season_type_id: int
    year: int

    def __init__(self):
        self.id = None
        self.season_type_id = None
        self.year = None

    @staticmethod
    def to_season(row: Row, prefix: str = "") -> Season:
        def get_value(key: str):
            return row[f"{prefix}.{key}"] if prefix else row[key]

        season = Season()
        season.id = get_value("id")
        season.season_type_id = get_value("season_type")
        season.year = get_value("year")

        return season
