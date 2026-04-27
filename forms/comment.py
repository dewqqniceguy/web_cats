from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class CommentForm(FlaskForm):
    rate = SelectField('Оценка', choices=[
        ('1', '1 - Ужасно'),
        ('2', '2 - Плохо'),
        ('3', '3 - Нормально'),
        ('4', '4 - Хорошо'),
        ('5', '5 - Отлично')
    ], validators=[DataRequired(message="Это поле обязательное")])
    content = TextAreaField('Комментарий', validators=[
        DataRequired(message="Это поле обязательное")
    ])
    submit = SubmitField('Оставить отзыв')