import click
import csv
import itertools
import os
import uuid

from flask import Flask, current_app
from flask.cli import with_appcontext
from sqlite3 import Cursor

from .db import get_db
from .models import User

filename = "picks.csv"


def get_team_ids(cursor: Cursor):
    cursor.execute("SELECT id, abbreviation FROM team;")

    rows = cursor.fetchall()

    team_ids = {}

    for row in rows:
        team_ids[row["abbreviation"]] = row["id"]

    return team_ids


def get_week_ids(cursor: Cursor):
    cursor.execute("SELECT id FROM week WHERE season_id = 1 ORDER BY number;")

    rows = cursor.fetchall()

    return [row["id"] for row in rows]


def get_user_id(first: str, last: str, cursor: Cursor):
    cursor.execute(
        """
        SELECT
            id
        FROM
            user
        WHERE
            first_name = :first_name AND
            last_name = :last_name
        LIMIT 1;
        """,
        {"first_name": first, "last_name": last},
    )

    row = cursor.fetchone()

    return row["id"] if row else None


def import_user(name: str, cursor: Cursor):
    [first, last] = name.split(" ", maxsplit=1)

    if first == "Andy" and last == "S":
        last = "Steinberg"

    existing_id = get_user_id(first, last, cursor)
    if existing_id:
        return existing_id

    user = User.from_dictionary(
        {
            "id": uuid.uuid4(),
            "first_name": first,
            "last_name": last,
            "email": f"{first}_{last}@fake.email",
        }
    )

    cursor.execute(
        """
        INSERT INTO user (id, email, first_name, last_name, nickname, password)
        VALUES (:id, :email, :first_name, :last_name, :nickname, :password);
        """,
        {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "nickname": user.nickname,
            "password": user.password,
        },
    )

    cursor.execute(
        "INSERT INTO season_participant (season_id, user_id) VALUES (:season_id, :user_id);",
        {"season_id": 1, "user_id": user.id},
    )

    return user.id


def create_pick(user_id: uuid.UUID, week_id: int, team_id: int, cursor: Cursor):
    cursor.execute(
        """
        INSERT INTO
            pick
                (week_id, user_id, team_id)
            VALUES
                (:week_id, :user_id, :team_id)
            ON CONFLICT DO NOTHING;
        """,
        {"week_id": week_id, "user_id": user_id, "team_id": team_id},
    )

    return cursor.lastrowid


def import_picks(
    user_id: uuid.UUID,
    team_ids: dict[str, int],
    week_ids: list[int],
    picks: list[str],
    cursor: Cursor,
):
    for (i, team) in enumerate(picks):
        if team not in team_ids:
            continue

        team_id = team_ids[team]
        create_pick(user_id, week_ids[i], team_id, cursor)


@click.command("import-csv")
@with_appcontext
def import_command():
    """Import users and picks from a csv file."""

    path = os.path.join(current_app.instance_path, filename)
    with open(path, newline="") as csvfile:
        rows = csv.DictReader(
            csvfile, fieldnames=["rank", "name", "wins", "losses"], restkey="picks"
        )

        db = get_db()
        cursor = db.cursor()

        team_ids = get_team_ids(cursor)
        week_ids = get_week_ids(cursor)

        for row in itertools.islice(rows, 1, None):
            id = import_user(row["name"], cursor)
            import_picks(id, team_ids, week_ids, row["picks"], cursor)

        db.commit()
        cursor.close()

        print("Import complete")


def init(app: Flask):
    app.cli.add_command(import_command)
