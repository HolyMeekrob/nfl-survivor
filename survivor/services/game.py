from survivor.api import GameState as ApiGameState
from survivor.data import Game, GameState
from survivor.utils.db import wrap_operation

from . import team as team_service

__gameStateMap = {
    ApiGameState.PREGAME: GameState.PREGAME,
    ApiGameState.IN_PROGRESS: GameState.IN_PROGRESS,
    ApiGameState.COMPLETE: GameState.COMPLETE,
}


@wrap_operation()
def get_by_week(week_id, *, cursor=None):
    cursor.execute(
        """
        SELECT
            *
        FROM
            game
        WHERE
            week_id = :week_id
        """,
        {"week_id": week_id},
    )

    games_raw = cursor.fetchall()

    return [Game.to_game(game) for game in games_raw]


@wrap_operation(is_write=True)
def create(week_id, game, *, cursor=None):
    away_team_id = team_service.get_by_name(game.away_team, cursor=cursor).id
    home_team_id = team_service.get_by_name(game.home_team, cursor=cursor).id

    if away_team_id == None or home_team_id == None:
        raise Exception

    state = __gameStateMap.get(game.State)

    cursor.execute(
        """
        INSERT INTO game (week_id, away_team_id, home_team_id, away_score, home_score, odds, kickoff, state)
        VALUES (:week_id, :away_team_id, :home_team_id, :away_score, :home_score, :odds, :kickoff, :state);
        """,
        {
            "week_id": week_id,
            "away_team_id": away_team_id,
            "home_team_id": home_team_id,
            "away_score": game.away_score or 0,
            "home_score": game.home_score or 0,
            "odds": game.odds,
            "kickoff": None if game.date == None else game.date.isoformat(),
            "state": state,
        },
    )

    id = cursor.lastrowid

    return id


@wrap_operation(is_write=True)
def update(game, *, cursor=None):
    cursor.execute(
        """
        UPDATE
            game
        SET
            away_team_id = :away_team_id,
            home_team_id = :home_team_id,
            away_score = :away_score,
            home_score = :home_score,
            odds = :odds,
            kickoff = :kickoff,
            state = :state
        WHERE
            id = :id
        """,
        {
            "id": game.id,
            "away_team_id": game.away_team_id,
            "home_team_id": game.home_team_id,
            "away_score": game.away_score,
            "home_score": game.home_score,
            "odds": game.odds,
            "kickoff": game.kickoff,
            "state": game.state,
        },
    )

    return game


@wrap_operation()
def get_by_matchup(away_team_id, home_team_id, year, week, *, cursor=None):
    cursor.execute(
        """
        SELECT
            game.*
        FROM
            game
        INNER JOIN
            week    ON game.week_id = week.id
        INNER JOIN
            season  ON week.season_id = season.id
        WHERE
            game.away_team_id   = :away_team_id AND
            game.home_team_id   = :home_team_id AND
            week.number         = :week         AND
            season.year         = :year
        """,
        {
            "away_team_id": away_team_id,
            "home_team_id": home_team_id,
            "week": week,
            "year": year,
        },
    )

    raw_games = cursor.fetchall()

    return [Game.to_game(game) for game in raw_games]


@wrap_operation(is_write=True)
def update_from_api(year, week, api_game, *, cursor=None):
    def get_updated_game(game):
        game.away_score = api_game.away_score or 0
        game.home_score = api_game.home_score or 0
        game.state = GameState(api_game.state.value)
        game.odds = api_game.odds if api_game.odds else game.odds
        game.kickoff = api_game.date if api_game.date else game.kickoff
        return game

    away_team_id = team_service.get_by_name(api_game.away_team, cursor=cursor).id
    home_team_id = team_service.get_by_name(api_game.home_team, cursor=cursor).id

    if away_team_id == None or home_team_id == None:
        raise Exception

    games = get_by_matchup(away_team_id, home_team_id, year, week, cursor=cursor)

    return [update(get_updated_game(game)) for game in games]
