from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto

from survivor.data import Team, User, Week


@dataclass
class _PickResult:
    user: User
    team: Team | None
    week: Week
    outcome: _PickOutcome


class _PickOutcome(Enum):
    CORRECT = auto()
    INCORRECT = auto()
    NOT_YET_DECIDED = auto()
