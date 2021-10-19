from datetime import datetime, timezone, timedelta
from .game import Game, GameState
from enum import Enum, auto
from html.parser import HTMLParser
import re


days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
months = [
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC",
]


def first(pred, lst):
    return next(filter(pred, lst), None)


def any_match(pred, lst):
    return first(pred, lst) != None


def has_class(attrs, _class):
    def class_is_included(name_val_pair):
        (name, val) = name_val_pair
        return name == "class" and _class in val

    return any_match(class_is_included, attrs)


def get_state(attrs):
    if has_class(attrs, "pregame"):
        return GameState.PREGAME

    if has_class(attrs, "ingame"):
        return GameState.IN_PROGRESS

    return GameState.COMPLETE


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.modes = [ProcessMode.NONE]
        self.parsers = {
            ProcessMode.NONE: NoneParser(),
            ProcessMode.GAME: GameParser(),
            ProcessMode.DATE: DateParser(),
            ProcessMode.TEAM: TeamParser(),
            ProcessMode.SCORE: ScoreParser(),
            ProcessMode.ODDS: OddsParser(),
        }
        self.games = []

    def get_mode(self):
        return self.modes[-1]

    def get_parser(self):
        return self.parsers[self.get_mode()]

    def handle_starttag(self, tag, attrs):
        mode = self.get_parser().handle_starttag(self, tag, attrs)
        if mode != None:
            self.modes.append(mode)

    def handle_endtag(self, tag):
        should_exit_mode = self.get_parser().handle_endtag(tag)
        if should_exit_mode:
            self.modes.pop()

    def handle_data(self, data):
        self.get_parser().handle_data(self, data)


class SubParser:
    def handle_starttag(self, root, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, root, data):
        pass


class NoneParser(SubParser):
    def handle_starttag(self, root, tag, attrs):
        if tag == "div" and has_class(attrs, "single-score-card"):
            game = Game()
            game.state = get_state(attrs)
            root.games.append(game)
            return ProcessMode.GAME

        return None


class GameParser(SubParser):
    def __init__(self):
        super().__init__()
        self.div_count = 0

    def handle_starttag(self, root, tag, attrs):

        if tag == "span" and has_class(attrs, "pregame-date"):
            return ProcessMode.DATE

        if tag == "a" and has_class(attrs, "team"):
            return ProcessMode.TEAM

        if tag == "td" and has_class(attrs, "total-score"):
            return ProcessMode.SCORE

        if tag == "td" and has_class(attrs, "in-progress-odds-home"):
            return ProcessMode.ODDS

        if tag == "div":
            self.div_count += 1

        return None

    def handle_endtag(self, tag):
        if tag == "div" and self.div_count == 0:
            return True

        if tag == "div":
            self.div_count -= 1

        return False


class DateParser(SubParser):
    @staticmethod
    def _get_day(day_of_week):
        now = datetime.now()

        delta = 0

        if day_of_week != None:
            delta = days.index(day_of_week) - now.weekday()
            delta = delta + 7 if delta < 0 else delta

        date = now + timedelta(days=delta)

        return (date.month, date.day)

    def handle_endtag(self, tag):
        return tag == "span"

    def handle_data(self, root, data):
        day_group = "|".join(days)
        month_group = "|".join(months)
        regex = re.compile(
            rf"(?:(?P<day_of_week>{day_group}) )?(?:(?P<month>{month_group}) )?(?:(?P<day>\d{{1,2}}), )?(?P<hour>\d{{1,2}}):(?P<minutes>\d{{2}})(?P<time_of_day>am|pm)"
        )
        match = regex.match(data.strip())

        # TODO: get year
        year = 2021
        eastern = timezone(timedelta(hours=-5))

        # Possible formats for games that have not started:
        # DOW MON DAY, HOUR:MINUTESam|pm (SUN JAN 9, 12:00pm) - Future week
        # DOW HOUR:MINUTESam|pm (SUN 12:00pm) - This week but not today
        # HOUR:MINUTESam|pm (12:00pm) - Today
        month_str = match.group("month")
        day_str = match.group("day")
        time_of_day = match.group("time_of_day")
        hours_to_add = 0 if time_of_day == "am" else 12

        (month, day) = (
            (months.index(match.group("month")) + 1, int(match.group("day")))
            if month_str != None and day_str != None
            else self._get_day(match.group("day_of_week"))
        )

        date = datetime(
            year,
            month,
            day,
            (int(match.group("hour")) + hours_to_add) % 24,
            int(match.group("minutes")),
            tzinfo=eastern,
        ).astimezone(timezone.utc)
        root.games[-1].date = date


class TeamParser(SubParser):
    def handle_endtag(self, tag):
        return tag == "a"

    def handle_data(self, root, data):
        root.games[-1].add_team(data)


class ScoreParser(SubParser):
    def handle_endtag(self, tag):
        return tag == "td"

    def handle_data(self, root, data):
        root.games[-1].add_score(int(data))


class OddsParser(SubParser):
    def handle_endtag(self, tag):
        return tag == "td"

    def handle_data(self, root, data):
        odds = None
        try:
            odds = float(data.strip())
        except ValueError:
            pass

        root.games[-1].odds = odds


class ProcessMode(Enum):
    NONE = auto()
    GAME = auto()
    DATE = auto()
    TEAM = auto()
    SCORE = auto()
    ODDS = auto()
