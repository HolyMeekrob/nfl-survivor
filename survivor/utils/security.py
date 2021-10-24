from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from itsdangerous.url_safe import URLSafeSerializer
from werkzeug.security import check_password_hash, generate_password_hash

__forgot_password_salt = "ugh-i-forgot"
__invitation_salt = "plz-let-me-in"


def __get_key():
    return current_app.config["SECRET_KEY"]


def __get_serializer():
    return URLSafeSerializer(__get_key())


def __get_timed_serializer():
    return URLSafeTimedSerializer(__get_key())


def __get_code(salt, value):
    serializer = __get_serializer()
    return serializer.dumps(value, salt=salt)


def __get_timed_code(salt, value):
    serializer = __get_timed_serializer()
    return serializer.dumps(value, salt=salt)


def __verify_code(salt, code):
    serializer = __get_serializer()
    return serializer.loads(code, salt=salt)


def __verify_timed_code(max_age, salt, code):
    serializer = __get_timed_serializer()
    return serializer.loads(code, max_age=max_age, salt=salt)


def get_forgot_password_code(email):
    return __get_timed_code(__forgot_password_salt, email)


def verify_forgot_password_code(code):
    max_age = current_app.config["FORGOT_PASSWORD_LINK_EXPIRATION"]
    return __verify_timed_code(max_age, __forgot_password_salt, code)


def get_invitation_code(email):
    return __get_code(__invitation_salt, email)


def verify_invitation_code(code):
    return __verify_code(__invitation_salt, code)


def create_password_hash(password):
    return generate_password_hash(password)


def verify_password_hash(password_hash, password):
    return check_password_hash(password_hash, password)
