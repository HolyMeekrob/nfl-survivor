from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField
from wtforms.fields import EmailField
from wtforms.validators import Email, DataRequired


class LoginForm(FlaskForm):
    name = EmailField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    remember = BooleanField(label="Remember me")
