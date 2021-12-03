from __future__ import annotations
from dataclasses import dataclass, field
from sqlite3 import Row

from .week_timer import WeekTimer


@dataclass
class Rules:
    id: int = 0
    max_strikes: int = 1
    max_team_picks: int = 1
    pick_cutoff: WeekTimer = WeekTimer.FIRST_GAME
    pick_reveal: WeekTimer = WeekTimer.FIRST_GAME
    entry_fee: float = 0
    winnings: list[float] = field(default_factory=lambda: [1])

    @staticmethod
    def to_rules(row: Row, prefix: str = "") -> Rules:
        def get_value(key: str):
            return row[f"{prefix}.{key}"] if prefix else row[key]

        rules = Rules()
        rules.id = get_value("id")
        rules.max_strikes = get_value("max_strikes")
        rules.max_team_picks = get_value("max_team_picks")
        rules.pick_cutoff = get_value("pick_cutoff")
        rules.pick_reveal = get_value("pick_reveal")
        rules.entry_fee = get_value("entry_fee")
        rules.winnings = get_value("winnings")

        return rules
