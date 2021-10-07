from survivor.data import get_db
from .game import create as create_game


def create(season_id, week, cursor=None):
    is_local_cursor = cursor == None
    db = None

    if is_local_cursor:
        db = get_db()
        cursor = db.cursor()

    cursor.execute(
        "INSERT INTO week (season_id, number) VALUES(:season_id, :number);",
        {"season_id": season_id, "number": week.number},
    )

    id = cursor.lastrowid

    for game in week.games:
        create_game(id, game, cursor)

    if is_local_cursor:
        db.commit()
        cursor.close()

    return id
