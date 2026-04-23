from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class QuantityForm(FlaskForm):
    quantity = IntegerField('Количество', validators=[DataRequired(), NumberRange(min=1, message="Не меньше 1")])
    submit = SubmitField('Сохранить')
