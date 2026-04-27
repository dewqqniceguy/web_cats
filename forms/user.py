from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange

class RegisterForm(FlaskForm):
    email = StringField('Почта', validators=[
        DataRequired(message="Это поле обязательное")
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Это поле обязательное"),
        Length(min=6, message="Пароль должен быть не менее 6 символов")
    ])
    password_again = PasswordField('Повторите пароль', validators=[
        DataRequired(message="Это поле обязательное"),
        EqualTo('password', message="Пароли не совпадают")
    ])
    name = StringField('Имя пользователя', validators=[
        DataRequired(message="Это поле обязательное")
    ])
    city = StringField('Город', validators=[
        DataRequired(message="Это поле обязательное")
    ])
    age = IntegerField('Возраст', validators=[
        DataRequired(message="Это поле обязательное"),
        NumberRange(min=0, max=150, message="Возраст должен быть от 0 до 150 лет")
    ])
    submit = SubmitField('Зарегистрироваться')