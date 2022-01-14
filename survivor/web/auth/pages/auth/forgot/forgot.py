from flask_wtf import FlaskForm
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email


class ForgotForm(FlaskForm):
    email = EmailField(validators=[DataRequired(), Email()])
