from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired


class PurchaseForm(FlaskForm):
    quantity = IntegerField("Количество", validators=[DataRequired()])
    submit = SubmitField('Добавить в корзину')
