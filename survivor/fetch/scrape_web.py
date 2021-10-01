from urllib.request import urlopen
from schedule_parser import Parser
from week import Week


def get_html(year, week):
    url = f"https://www.cbssports.com/nfl/scoreboard/all/{year}/regular/{week}/"
    with urlopen(url) as response:
        return response.read().decode()


def get_games(html):
    p = Parser()
    p.feed(html)
    return p.games


def run(year, week):
    html = get_html(year, week)
    return Week(week, get_games(html))


# weeks = [run(2021, week) for week in range(3, 4)]
# print("\n\n\n".join(list(map(str, weeks))))
