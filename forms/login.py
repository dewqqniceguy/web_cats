from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[
        DataRequired(message="Это поле обязательное")
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Это поле обязательное")
    ])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')