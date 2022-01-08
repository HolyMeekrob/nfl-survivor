import os

from flask import Flask, redirect, render_template, request, url_for
from flask_apscheduler import APScheduler
from flask_login import LoginManager, current_user
from pytz import utc

from survivor.services.pick import get_picks_for_week
from survivor.utils.datetime import utcnow
from survivor.utils.email import send_user_email
from survivor.web.admin.emails import MissingPickEmailModel

from .data import User, db, import_csv
from .services import (
    rules as rules_service,
    scoring as scoring_service,
    season as season_service,
    user as user_service,
    week as week_service,
    week_timer as week_timer_service,
)
from .web import admin, auth, home


def __start_scheduled_tasks(app: Flask):
    # schedule tasks
    scheduler = APScheduler()

    @scheduler.task(
        "interval",
        id="update_season",
        name="Updates the current season's games from the API",
        coalesce=True,
        max_instances=1,
        misfire_grace_time=int(app.config["UPDATE_FROM_API_INTERVAL_SECONDS"] / 2),
        seconds=app.config["UPDATE_FROM_API_INTERVAL_SECONDS"],
    )
    def update_season():
        with scheduler.app.app_context():
            year = utcnow().year
            seasons = season_service.get_by_year(year)

            if seasons:
                season_service.update_games(seasons[0].id)

    @scheduler.task(
        "cron",
        id="alert_missing_picks",
        name="Alerts users who have yet to enter a pick for the current week",
        coalesce=True,
        max_instances=1,
        misfire_grace_time=60 * 60,
        hour=0,
        timezone=utc,
    )
    def alert_missing_picks():
        with scheduler.app.app_context():
            cursor = db.get_db().cursor()
            seasons = season_service.get_current_seasons(cursor=cursor)

            if not seasons:
                return

            season = seasons[0]
            week = week_service.get_current_week(season.id, cursor=cursor)
            rules = rules_service.get(season.id, cursor=cursor)

            deadline = week_timer_service.get_deadline(
                week.id, rules.pick_cutoff, cursor=cursor
            )
            now = utcnow()

            if deadline <= now:
                return

            participants = {
                participant.id
                for participant in season_service.get_participants(
                    season.id, cursor=cursor
                )
            }
            participants_with_a_pick = {
                pick.user_id for pick in get_picks_for_week(week.id, cursor=cursor)
            }

            eliminated_users = {
                standing[0].user.id
                for standing in scoring_service.get_standings(season.id, cursor=cursor)
                if standing[0].is_eliminated()
            }

            participants_without_a_pick = participants.difference(
                participants_with_a_pick.union(eliminated_users)
            )

            for participant in list(participants_without_a_pick)[0:1]:
                user = user_service.get(participant, cursor=cursor)
                message = render_template(
                    "admin/emails/admin/missing_pick/missing_pick.html",
                    model=MissingPickEmailModel(
                        user.name, app.config["APP_NAME"], deadline
                    ),
                )

                send_user_email(
                    user, "You have not yet entered a pick for this week", message
                )

    scheduler.init_app(app)
    scheduler.start()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="web",
        static_folder="web/static",
    )
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "survivor.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.before_request
    def require_authentication():
        is_static = request.endpoint and request.endpoint.startswith("static")
        is_authenticated = current_user.is_authenticated
        is_public = request.endpoint and getattr(
            app.view_functions[request.endpoint], "is_public", False
        )

        if any([is_static, is_authenticated, is_public]):
            return
        else:
            return redirect(url_for("auth.get_login"))

    # initialize the database
    db.init(app)

    # initialize csv import command
    import_csv.init(app)

    # initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.get_login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return user_service.get(id)

    # register blueprints
    app.register_blueprint(admin)
    app.register_blueprint(auth)
    app.register_blueprint(home)

    if app.env == "production":
        __start_scheduled_tasks(app)

    # ensure config users
    db_conn = db.get_db(app)
    cursor = db_conn.cursor()

    for user in app.config["INITIAL_USERS"]:
        try:
            user_service.create(
                User.from_dictionary(user), password_is_hashed=False, cursor=cursor
            )

            db_conn.commit()
        except:
            pass

    cursor.close()
    db_conn.close()

    return app
