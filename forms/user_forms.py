from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from data.users import User
from data import db_session


class RegistrationForm(FlaskForm):
    username = StringField('Логин',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль',
                                     validators=[DataRequired(), EqualTo('password')])

    first_name = StringField('Имя')
    last_name = StringField('Фамилия')
    phone = StringField('Номер телефона')

    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter_by(username=username.data).first()
        db_sess.close()

        if user:
            raise ValidationError('Пользователь с таким именем уже существует')

    def validate_email(self, email):
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter_by(email=email.data).first()
        db_sess.close()

        if user:
            raise ValidationError('Пользователь с таким email уже существует')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Вход')
