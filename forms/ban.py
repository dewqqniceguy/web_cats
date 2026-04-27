from flask_wtf import FlaskForm
from wtforms.fields.simple import SubmitField, StringField
from wtforms.validators import DataRequired

class BanForm(FlaskForm):
    reason = StringField('Причина бана', validators=[
        DataRequired(message="Это поле обязательное")
    ])
    submit = SubmitField('Забанить')