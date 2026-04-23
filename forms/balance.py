from flask_wtf import FlaskForm
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired


class BalanceForm(FlaskForm):
    balance = IntegerField('Рубли', validators=[DataRequired()])
    submit = SubmitField('Пополнить баланс')
