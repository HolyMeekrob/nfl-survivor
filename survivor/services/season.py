from survivor.data import get_db, Season, SeasonType, Week
from survivor.api import get_season as fetch_season
from .week import create as create_week


def get_seasons():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM season")
    seasons_raw = cursor.fetchall()

    cursor.close()
    return [Season.to_season(season) for season in seasons_raw]


def create(year):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO season (season_type, year) VALUES(:season_type, :year);",
        {"season_type": SeasonType.REGULAR.value, "year": year},
    )

    id = cursor.lastrowid

    weeks = fetch_season(year)

    for week in weeks:
        create_week(id, week, cursor)

    db.commit()
    cursor.close()

    return id


def get(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("pragma short_column_names=OFF;")
    cursor.execute("pragma full_column_names=ON;")
    cursor.execute(
        """
        SELECT *
        FROM season
        LEFT JOIN week ON season.id = week.season_id
        WHERE season.id = :id;
        """,
        {"id": id},
    )

    weeks_raw = cursor.fetchall()

    if not weeks_raw:
        return None

    season = Season.to_season(weeks_raw[0], "season")
    season.weeks = [Week.to_week(week, "week") for week in weeks_raw]

    cursor.close()

    return season
