from urllib.request import urlopen
from .schedule_parser import Parser
from .week import Week


def get_html(year, week):
    url = f"https://www.cbssports.com/nfl/scoreboard/all/{year}/regular/{week}/"
    with urlopen(url) as response:
        return response.read().decode()


def get_games(html):
    p = Parser()
    p.feed(html)
    return p.games


def get_week(year, week):
    html = get_html(year, week)
    return Week(week, get_games(html))


def get_season(year):
    # TODO: get this value programmatically
    num_weeks = 18
    return [get_week(2021, week) for week in range(1, num_weeks + 1)]


# weeks = [get_week(2021, week) for week in range(3, 4)]
# print("\n\n\n".join(list(map(str, weeks))))
