from dataclasses import dataclass
from survivor.data.models import User


@dataclass
class ChampionCrownedEmailModel:
    user_name: str
    league_name: str
    champions: list[str]
