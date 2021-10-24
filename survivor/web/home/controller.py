from flask import Blueprint, render_template

home = auth = Blueprint("home", __name__, template_folder="pages")


@home.get("/")
def index():
    return render_template("home.html")


@home.get("/invitations")
def my_invitations():
    return render_template("invitations/invitations.html")
