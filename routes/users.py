from flask import render_template, url_for, flash, redirect, request

from data.goods import Category
from main import app
from werkzeug.security import generate_password_hash, check_password_hash
from data import db_session
from forms.user_forms import RegistrationForm, LoginForm
from data.users import User
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/register", methods=['GET', 'POST'])
def register():
    db_sess = db_session.create_session()

    if current_user.is_authenticated:
        return redirect(url_for('index_page'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)

        user = User(username=form.username.data,
                    email=form.email.data,
                    hashed_password=hashed_password,
                    phone=form.phone.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data)

        db_sess.add(user)
        db_sess.commit()
        db_sess.close()

        flash('Ваш аккаунт был создан. Теперь вы можете войти!', 'success')
        return redirect(url_for('login'))

    categories = db_sess.query(Category).filter_by(parent_id=None)
    db_sess.close()
    return render_template('register.html',
                           title='Register',
                           form=form,
                           categories=categories)


@app.route("/login", methods=['GET', 'POST'])
def login():
    db_sess = db_session.create_session()

    if current_user.is_authenticated:
        return redirect(url_for('index_page'))

    form = LoginForm()

    if form.validate_on_submit():
        user = db_sess.query(User).filter_by(email=form.email.data).first()

        if user and check_password_hash(user.hashed_password, form.password.data):
            login_user(user, remember=form.remember.data)
            db_sess.close()

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index_page'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    categories = db_sess.query(Category).filter_by(parent_id=None)

    db_sess.close()
    return render_template('login.html',
                           title='Login',
                           form=form,
                           categories=categories)


@app.route("/logout")
def logout():
    db_sess = db_session.create_session()
    logout_user()
    db_sess.close()

    return redirect(url_for('index_page'))


@app.route("/account")
@login_required
def account():
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).filter_by(parent_id=None)
    db_sess.close()

    return render_template('account.html', title='Account', categories=categories)