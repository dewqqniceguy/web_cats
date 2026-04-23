from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, SubmitField, FloatField, BooleanField
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    title = StringField('Имя котика / Заголовок', validators=[DataRequired()])
    content = TextAreaField("Описание (характер, привычки)")
    price = FloatField("Цена в ₽", validators=[DataRequired()])
    quantity = IntegerField("Количество", validators=[DataRequired()])

    # Характеристики котика
    breed = StringField('Порода (или "Беспородный")', validators=[DataRequired()])
    color = StringField('Окрас', validators=[DataRequired()])
    age_months = IntegerField('Возраст (в месяцах)', validators=[DataRequired()])
    gender = SelectField('Пол', choices=[('boy', 'Мальчик'), ('girl', 'Девочка')], validators=[DataRequired()])
    vaccinated = BooleanField("Привит(а)")

    image = FileField('Фотография котика')
    submit = SubmitField('Разместить котика')