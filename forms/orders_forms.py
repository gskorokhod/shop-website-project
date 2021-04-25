from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired


class OrderForm(FlaskForm):
    country = StringField('Страна', validators=[DataRequired()])
    city = StringField('Город', validators=[DataRequired()])
    street = StringField('Улица', validators=[DataRequired()])
    building = StringField('Дом', validators=[DataRequired()])
    entrance = StringField('Подъезд')
    floor = StringField('Этаж')
    flat = StringField('Квартира')

    description = TextAreaField('Описание')
    delivery_date = DateField('Дата доставки', format='%Y-%m-%d', validators=[DataRequired()])

    submit = SubmitField('Оформить заказ')
