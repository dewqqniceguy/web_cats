from flask_wtf import FlaskForm
from wtforms.fields.simple import SubmitField, StringField
from wtforms.validators import DataRequired


class BanForm(FlaskForm):
    password_for_ban = StringField('Подтвердите действие', validators=[DataRequired()])
    reason = StringField('Причина бана', validators=[DataRequired()])
    submit = SubmitField('Забанить')
