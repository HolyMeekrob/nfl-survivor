import os
import sqlite3
import uuid

import click
from flask import current_app, g
from flask.cli import with_appcontext

from .migrate import migrate
from .models import GameState


def __get_db_location(app):
    return app.config["DATABASE"]


def __get_new_db(app):
    db = sqlite3.connect(__get_db_location(app), detect_types=sqlite3.PARSE_DECLTYPES)

    db.row_factory = sqlite3.Row
    return db


def get_db(app=None):
    if app:
        return __get_new_db(app)

    if "db" not in g:
        g.db = __get_new_db(current_app)

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


@click.command("migrate-db")
@with_appcontext
def migrate_db_command():
    """Run pending database migration scripts"""
    (old, new) = migrate(current_app, get_db())

    if old == new:
        click.echo(f"Database is already on the latest version ({old})")
    elif old == -1:
        click.echo(f"Database initialized to version {new}")
    else:
        click.echo(f"Migrated database from version {old} to version {new}")


@click.command("rebuild-db")
@with_appcontext
def rebuild_db_command():
    """Rebuild the database from scratch. All non-static data will be lost."""
    os.remove(__get_db_location(current_app))
    (_, new) = migrate(current_app, get_db())
    click.echo(f"Database rebuilt to version {new}")


def register_uuid():
    sqlite3.register_converter("UUID", lambda b: uuid.UUID(bytes_le=b))
    sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)


def register_game_state():
    sqlite3.register_converter(
        "GAME_STATE",
        lambda name: GameState[name.decode()]
        if isinstance(name, bytes)
        else GameState[name],
    )
    sqlite3.register_adapter(GameState, lambda state: state.name)


def init(app):
    register_uuid()
    register_game_state()

    app.teardown_appcontext(close_db)
    app.cli.add_command(migrate_db_command)
    app.cli.add_command(rebuild_db_command)
