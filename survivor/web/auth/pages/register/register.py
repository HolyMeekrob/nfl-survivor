from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, DataRequired


class RegisterForm(FlaskForm):
    email = EmailField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    is_email_read_only = HiddenField()
