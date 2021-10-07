from survivor.data import get_db
from .team import get_by_name as get_team_by_name


def create(week_id, game, cursor=None):
    is_local_cursor = cursor == None
    db = None

    if is_local_cursor:
        db = get_db()
        cursor = db.cursor()

    away_team_id = get_team_by_name(game.away_team).id
    home_team_id = get_team_by_name(game.home_team).id

    if away_team_id == None or home_team_id == None:
        raise Exception

    cursor.execute(
        """
        INSERT INTO game (week_id, away_team_id, home_team_id, away_score, home_score, odds, kickoff, is_complete)
        VALUES (:week_id, :away_team_id, :home_team_id, :away_score, :home_score, :odds, :kickoff, :is_complete);
        """,
        {
            "week_id": week_id,
            "away_team_id": away_team_id,
            "home_team_id": home_team_id,
            "away_score": game.away_score or 0,
            "home_score": game.home_score or 0,
            "odds": game.odds,
            "kickoff": None if game.date == None else game.date.isoformat(),
            "is_complete": game.is_complete or False,
        },
    )

    id = cursor.lastrowid

    if is_local_cursor:
        db.commit()
        cursor.close()

    return id
