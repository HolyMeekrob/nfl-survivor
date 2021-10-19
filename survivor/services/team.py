from survivor.data import Team
from survivor.utils.db import wrap_operation


@wrap_operation()
def get_by_name(name, *, cursor=None):
    cursor.execute("SELECT * FROM team WHERE name = :name", {"name": name})
    row = cursor.fetchone()

    team = None
    if cursor != None:
        team = Team.to_team(row)

    return team
