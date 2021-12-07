from datetime import datetime
import os

from flask import Flask, redirect, request, url_for
from flask_apscheduler import APScheduler
from flask_login import LoginManager, current_user

from .data import db, import_csv, User
from .services import season as season_service, user as user_service
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
            year = datetime.utcnow().year
            seasons = season_service.get_by_year(year)

            if seasons:
                season_service.update_games(seasons[0].id)

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
