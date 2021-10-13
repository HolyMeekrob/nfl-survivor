from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_user, logout_user
from itsdangerous import SignatureExpired

from survivor.services import user as user_service
from survivor.utils.email import send_email
from survivor.utils.security import (
    get_forgot_password_code,
    verify_forgot_password_code,
    verify_password_hash,
)
from .emails import ForgotPasswordEmailModel
from .pages import ForgotForm, LoginForm, ResetForm

auth = Blueprint("auth", __name__, template_folder=".")


def login(form):
    return render_template("pages/login/login.html", form=form)


@auth.get("/login")
def get_login():

    return (
        redirect(url_for("home.index"))
        if current_user.is_authenticated
        else login(LoginForm())
    )


@auth.post("/login")
def post_login():
    form = LoginForm()

    if not form.validate():
        return login(form)

    email = form.name.data
    password = form.password.data
    user = user_service.get_by_email(email)

    if not user or not verify_password_hash(user.password, password):
        flash("Error logging in")
        return login(form)

    login_user(user, remember=form.remember.data)
    url = url_for(request.args.get("redirect") or "home.index")
    return redirect(url)


@auth.get("/logout")
def logout():
    logout_user()
    return redirect(url_for("home.index"))


@auth.get("/register")
def register():
    return "Register new account"


def forgot(form):
    return render_template("pages/forgot/forgot.html", form=form)


@auth.get("/forgot-password")
def get_forgot():
    return (
        redirect(url_for("home.index"))
        if current_user.is_authenticated
        else forgot(ForgotForm())
    )


@auth.post("/forgot-password")
def post_forgot():
    form = ForgotForm()

    if not form.validate():
        return forgot(form)

    email = form.email.data
    user = user_service.get_by_email(email)

    # If user does not exist, pretend an email was sent
    # Otherwise a bad actor could figure out which email addresses are in use
    if not user:
        return forgot(None)

    code = get_forgot_password_code(email)

    message = render_template(
        "emails/forgot/forgot.html",
        model=ForgotPasswordEmailModel(
            email, code, int(current_app.config["FORGOT_PASSWORD_LINK_EXPIRATION"] / 60)
        ),
    )

    send_email(user, f"{current_app.config['APP_NAME']} - Password Reset", message)

    # TODO: update user to indicate that there is a valid forgot password code

    return forgot(None)


def reset(form):
    return render_template("pages/reset/reset.html", form=form)


@auth.get("/reset-password")
def get_reset():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    form = ResetForm()
    form.code.data = request.args.get("code")
    return reset(form)


@auth.post("/reset-password")
def post_reset():
    def handle_error(msg):
        flash(f"{msg} Please submit a new forgot password request")
        return reset(None)

    form = ResetForm()

    if not form.validate():
        return reset(form)

    try:
        email = verify_forgot_password_code(form.code.data)

    except SignatureExpired:
        return handle_error("The given code has expired.")

    except:
        return handle_error("There was an error processing your request.")

    user = user_service.get_by_email(email)

    if not user:
        return handle_error("There was an error processing your request.")

    password = form.password.data
    user.password = password

    try:
        user_service.save(user, password_is_hashed=False)

    except:
        return handle_error("There was an error updating your password.")

    return redirect(url_for("auth.get_login"))
