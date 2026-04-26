from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, Optional

class ProductForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField('Описание', validators=[DataRequired()])
    price = FloatField('Цена (₽)', validators=[DataRequired()])
    breed = StringField('Порода', validators=[DataRequired()])
    color = StringField('Окрас', validators=[DataRequired()])
    age_months = IntegerField('Возраст (месяцев)', validators=[DataRequired()])
    gender = SelectField('Пол', choices=[('male', 'Мальчик'), ('female', 'Девочка')], validators=[DataRequired()])
    vaccinated = SelectField('Привит(а)', choices=[('yes', 'Да'), ('no', 'Нет')], validators=[DataRequired()])
    image = FileField('Фото кота', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Разрешены только изображения!'),
        Optional()  # Теперь поле необязательное
    ])