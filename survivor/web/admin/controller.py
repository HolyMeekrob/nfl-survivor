from datetime import datetime
from flask import Blueprint, abort, flash, redirect, render_template, url_for

from survivor.services import season as season_service, week as week_service

admin = Blueprint("admin", __name__, url_prefix="/admin", template_folder="pages")


@admin.get("/")
def index():
    return render_template("index.html")


@admin.get("/seasons")
def seasons():
    return render_template("seasons.html", seasons=season_service.get_seasons())


@admin.get("/season/<int:id>")
def season(id):
    model = season_service.get(id)
    model.weeks = week_service.get_by_season(id)

    if not model:
        return abort(404)

    return render_template("season.html", season=model)


@admin.post("/season")
def create_season():
    year = datetime.utcnow().year

    try:
        id = season_service.create(year)

    except Exception:
        flash("Error creating season")
        return redirect(url_for("admin.seasons"))

    return redirect(url_for("admin.season", id=id))


@admin.post("/season/update-games/<int:id>")
def update_games(id):
    updated_games = season_service.update_games(id)

    if updated_games:
        flash("Games updated")
    else:
        flash("No games needed updating")

    return season(id)
