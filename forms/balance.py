from flask_wtf import FlaskForm
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, NumberRange

class BalanceForm(FlaskForm):
    balance = IntegerField('Рубли', validators=[
        DataRequired(message="Это поле обязательное"),
        NumberRange(min=1, message="Сумма должна быть больше 0")
    ])
    submit = SubmitField('Пополнить баланс')