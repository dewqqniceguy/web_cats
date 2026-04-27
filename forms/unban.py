from flask_wtf import FlaskForm
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired


class UnbanForm(FlaskForm):
    submit = SubmitField('Разблокировать')