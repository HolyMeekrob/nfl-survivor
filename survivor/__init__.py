import os

from flask import Flask
from flask_login import LoginManager

from .data import db, User
from .services import user as user_service
from .web import admin, auth, home


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

    # initialize the database
    db.init(app)

    # initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return user_service.get(id)

    # register blueprints
    app.register_blueprint(admin)
    app.register_blueprint(auth)
    app.register_blueprint(home)

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
