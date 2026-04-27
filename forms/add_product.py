from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, IntegerField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class AddProductForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField('Описание', validators=[DataRequired()])
    price = FloatField('Цена (в рублях)', validators=[DataRequired(), NumberRange(min=0)])
    breed = StringField('Порода', validators=[DataRequired()])
    color = StringField('Окрас', validators=[DataRequired()])
    age_months = IntegerField('Возраст (месяцев)', validators=[DataRequired(), NumberRange(min=0)])
    gender = SelectField('Пол', choices=[('male', 'Мальчик'), ('female', 'Девочка')], validators=[DataRequired()])
    vaccinated = SelectField('Привит', choices=[('yes', 'Да'), ('no', 'Нет')], validators=[DataRequired()])
    image = FileField('Фото кота', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения!')])
    submit = SubmitField('Добавить кота')