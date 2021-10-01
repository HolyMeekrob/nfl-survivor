from datetime import datetime
import operator
import os
import re

migrations_dir = "data/migrations"

get_number = operator.itemgetter("number")


def get_migration_number(filename):
    return int(re.match("^(\d+)", filename).group(0))


def get_file_info(filename):
    return {
        "path": os.path.join(migrations_dir, filename),
        "number": get_migration_number(filename),
    }


def get_current_version(db):
    cursor = db.cursor()
    cursor.execute("SELECT MAX(version) AS version FROM migration;")
    row = cursor.fetchone()
    current_version = int(row["version"])
    cursor.close()

    return current_version


def run_migrations(app, db, migrations):
    cursor = db.cursor()

    # run scripts
    for migration in migrations:
        with app.open_resource(migration["path"]) as script:
            cursor.executescript(script.read().decode("utf8"))

    # update migrations table
    new_version = get_number(migrations[-1])
    cursor.execute(
        "INSERT INTO migration (version, timestamp) VALUES (:version, :timestamp);",
        {
            "version": new_version,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

    db.commit()
    cursor.close()

    return new_version


def migrate(app, db):
    dir = os.path.join(app.root_path, migrations_dir)
    files = map(get_file_info, os.listdir(dir))

    try:
        current_version = get_current_version(db)

    except:
        current_version = -1

    file_is_included = lambda file_info: get_number(file_info) > current_version
    migrations = sorted(filter(file_is_included, files), key=get_number)

    if not migrations:
        return (current_version, current_version)

    new_version = run_migrations(app, db, migrations)

    return (current_version, new_version)
