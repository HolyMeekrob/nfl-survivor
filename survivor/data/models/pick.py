from __future__ import annotations
from dataclasses import dataclass
from sqlite3 import Row
from uuid import UUID


@dataclass
class Pick:
    week_id: int
    user_id: UUID
    team_id: int

    @staticmethod
    def to_pick(row: Row, prefix: str = ""):
        def get_value(key: str):
            return row[f"{prefix}.{key}"] if prefix else row[key]

        pick = Pick(get_value("week_id"), get_value("user_id"), get_value("team_id"))

        return pick
