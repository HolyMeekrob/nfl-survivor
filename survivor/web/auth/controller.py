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
from urllib.parse import urljoin, urlparse

from survivor.data import User
from survivor.services import user as user_service
from survivor.utils.email import send_user_email
from survivor.utils.security import (
    get_forgot_password_code,
    verify_forgot_password_code,
    verify_invitation_code,
    verify_password_hash,
)
from survivor.utils.web import public_route
from .emails import ForgotPasswordEmailModel
from .pages import ForgotForm, LoginForm, RegisterForm, ResetForm

auth = Blueprint("auth", __name__, template_folder=".")


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def go_home():
    return redirect(url_for("home.index"))


def login(form):
    return render_template("pages/auth/login/login.html", form=form)


@auth.get("/login")
@public_route
def get_login():
    return go_home() if current_user.is_authenticated else login(LoginForm())


@auth.post("/login")
@public_route
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

    next = request.args.get("next")

    return redirect(next) if next and is_safe_url(next) else go_home()


@auth.get("/logout")
def logout():
    logout_user()
    return go_home()


def register(form):
    return render_template("pages/auth/register/register.html", form=form)


@auth.get("/register")
@public_route
def get_register():
    if current_user.is_authenticated:
        return go_home()

    form = RegisterForm()

    code = request.args.get("code")

    email = ""
    if code:
        email = verify_invitation_code(code)

    form.email.data = email or ""
    form.is_email_read_only.data = bool(email)

    return register(form)


@auth.post("/register")
@public_route
def post_register():
    form = RegisterForm()

    if not form.validate():
        return register(form)

    email = form.email.data
    password = form.password.data

    user = user_service.get_by_email(email)

    if user and user.password:
        flash("User is already registered")
        return register(form)

    if user:
        user.password = password
        user_service.update(user, password_is_hashed=False)

    else:
        user = User.from_dictionary({"email": email, "password": password})
        user_id = user_service.create(user, password_is_hashed=False)
        user = user_service.get(user_id)

    login_user(user)

    next = request.args.get("next")

    return redirect(next) if next and is_safe_url(next) else go_home()


def forgot(form):
    return render_template("pages/auth/forgot/forgot.html", form=form)


@auth.get("/forgot-password")
@public_route
def get_forgot():
    return go_home() if current_user.is_authenticated else forgot(ForgotForm())


@auth.post("/forgot-password")
@public_route
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
        "emails/auth/forgot/forgot.html",
        model=ForgotPasswordEmailModel(
            email, code, int(current_app.config["FORGOT_PASSWORD_LINK_EXPIRATION"] / 60)
        ),
    )

    send_user_email(user, "password reset", message)

    # TODO: update user to indicate that there is a valid forgot password code

    return forgot(None)


def reset(form):
    return render_template("pages/auth/reset/reset.html", form=form)


@auth.get("/reset-password")
@public_route
def get_reset():
    if current_user.is_authenticated:
        return go_home()

    form = ResetForm()
    form.code.data = request.args.get("code")
    return reset(form)


@auth.post("/reset-password")
@public_route
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
        user_service.update(user, password_is_hashed=False)

    except:
        return handle_error("There was an error updating your password.")

    return redirect(url_for("auth.get_login"))
