from survivor.data import get_db, Team


def get_by_name(name):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM team WHERE name = :name", {"name": name})
    row = cursor.fetchone()

    team = None
    if cursor != None:
        team = Team.to_team(row)

    cursor.close()
    return team
