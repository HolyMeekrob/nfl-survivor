import os
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from .migrate import migrate


def get_db_location(app):
    return app.config["DATABASE"]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            get_db_location(current_app), detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

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
    os.remove(get_db_location(current_app))
    (_, new) = migrate(current_app, get_db())
    click.echo(f"Database rebuilt to version {new}")


def init(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(migrate_db_command)
    app.cli.add_command(rebuild_db_command)
