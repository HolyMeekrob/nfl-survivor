from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField
from wtforms.validators import DataRequired


class ResetForm(FlaskForm):
    password = PasswordField(validators=[DataRequired()])
    code = HiddenField()
