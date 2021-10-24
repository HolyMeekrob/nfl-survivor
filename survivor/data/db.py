import os
import sqlite3
import uuid

import click
from flask import current_app, g
from flask.cli import with_appcontext

from .migrate import migrate
from .models import GameState, InvitationStatus


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


def __register_uuid():
    sqlite3.register_converter("UUID", lambda b: uuid.UUID(bytes_le=b))
    sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)


def __register_enum(enum_type, sql_type):
    sqlite3.register_converter(
        sql_type,
        lambda name: enum_type[name.decode()]
        if isinstance(name, bytes)
        else enum_type[name],
    )

    sqlite3.register_adapter(enum_type, lambda enum_val: enum_val.name)


def init(app):
    __register_uuid()
    __register_enum(GameState, "GAME_STATE")
    __register_enum(InvitationStatus, "INVITATION_STATUS")

    app.teardown_appcontext(close_db)
    app.cli.add_command(migrate_db_command)
    app.cli.add_command(rebuild_db_command)
