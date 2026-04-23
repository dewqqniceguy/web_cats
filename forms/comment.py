from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    rate = SelectField('Оценка', choices=[
        (1, '1 звезда'),
        (2, '2 звезды'),
        (3, '3 звезды'),
        (4, '4 звезды'),
        (5, '5 звезд')
    ], validators=[DataRequired()])
    content = StringField('Отзыв', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')