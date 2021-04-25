from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class LocationForm(FlaskForm):
    country = StringField('Страна', validators=[DataRequired()])
    city = StringField('Город', validators=[DataRequired()])
    street = StringField('Улица', validators=[DataRequired()])
    building = StringField('Дом', validators=[DataRequired()])
    entrance = StringField('Подъезд')
    floor = StringField('Этаж')
    flat = StringField('Квартира')
