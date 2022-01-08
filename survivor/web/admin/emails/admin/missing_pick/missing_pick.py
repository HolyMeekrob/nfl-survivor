from dataclasses import dataclass
from datetime import datetime


@dataclass
class MissingPickEmailModel:
    user_name: str
    league_name: str
    deadline: datetime
