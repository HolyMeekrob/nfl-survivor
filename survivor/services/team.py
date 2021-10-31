from sqlite3 import Cursor

from survivor.data import Team
from survivor.utils.db import wrap_operation


@wrap_operation()
def get_all(*, cursor: Cursor = None):
    cursor.execute("SELECT * FROM team;")
    raw_teams = cursor.fetchall()

    return [Team.to_team(team) for team in raw_teams]


@wrap_operation()
def get_by_name(name: str, *, cursor: Cursor = None):
    cursor.execute("SELECT * FROM team WHERE name = :name;", {"name": name})
    row = cursor.fetchone()

    team = None
    if cursor != None:
        team = Team.to_team(row)

    return team
