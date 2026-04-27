from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, IntegerField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class AddProductForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(message="Это поле обязательное")])
    content = TextAreaField('Описание', validators=[DataRequired(message="Это поле обязательное")])
    price = FloatField('Цена (в рублях)', validators=[
        DataRequired(message="Это поле обязательное"),
        NumberRange(min=0, message="Цена не может быть отрицательной")
    ])
    breed = StringField('Порода', validators=[DataRequired(message="Это поле обязательное")])
    color = StringField('Окрас', validators=[DataRequired(message="Это поле обязательное")])
    age_months = IntegerField('Возраст (месяцев)', validators=[
        DataRequired(message="Это поле обязательное"),
        NumberRange(min=0, message="Возраст не может быть отрицательным")
    ])
    gender = SelectField('Пол', choices=[('male', 'Мальчик'), ('female', 'Девочка')],
                         validators=[DataRequired(message="Это поле обязательное")])
    vaccinated = SelectField('Привит', choices=[('yes', 'Да'), ('no', 'Нет')],
                             validators=[DataRequired(message="Это поле обязательное")])
    image = FileField('Фото кота', validators=[
        FileRequired(message="Это поле обязательное"),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения!')
    ])
    submit = SubmitField('Добавить кота')