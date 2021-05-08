import uuid

from flask import request, render_template, abort, session, jsonify, redirect, url_for, flash
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from data.users import User
from api_resorces.goods_resources import parse_goods_data
from tools import paginate, ru_format_str_time
from data import db_session
from app import app
from flask_login import current_user, login_required

from data.goods import Goods, Category, CharacteristicsType
from data.reviews import Review


@app.route('/categories')
def categories_page():
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).filter_by(parent_id=None)

    template = render_template('categories_page.html',
                               categories=categories,
                               title='Main')

    db_sess.close()
    return template


@app.route('/all_goods')
def all_goods_page():
    page = request.args.get('page', 1, type=int)

    db_sess = db_session.create_session()
    categories = db_sess.query(Category).filter_by(parent_id=None)
    query = db_sess.query(Goods)
    goods = paginate(query, page, 6)

    template = render_template('goods_list_page.html',
                               title=f'Все товары',
                               goods_items=goods,
                               category='all',
                               categories=categories)

    db_sess.close()
    return template


@app.route('/add_goods', methods=['GET', 'POST'])
@app.route('/goods/edit', methods=['GET', 'POST'])
@login_required
def goods_add_page():
    if not current_user.is_admin:
        abort(403)

    goods_id = request.args.get('goods_id', None, type=int)

    if request.method == 'GET':
        db_sess = db_session.create_session()

        categories = db_sess.query(Category).all()
        char_types = db_sess.query(CharacteristicsType).all()

        goods = None
        if goods_id:
            goods = db_sess.query(Goods).get(goods_id)

        template = render_template('goods_edit_page.html',
                                   categories=categories,
                                   char_types=char_types,
                                   goods=goods,
                                   errors={})
        db_sess.close()
        return template
    elif request.method == 'POST':
        form = request.form
        char_items = request.form.getlist('characteristic[]')
        categ_items = request.form.getlist('category[]')
        name = form['goodsName']
        description = form['description']
        price = form['price']
        amount = form['amount']
        bonus_points = form['bonus_points']

        errors = {}

        if not name:
            errors['name'] = ['Пожалуйста, заполните это поле!']
        if not price:
            errors['price'] = ['Пожалуйста, заполните это поле!']
        if not amount:
            errors['amount'] = ['Пожалуйста, заполните это поле!']

        if not str(price).isalnum():
            errors['price'] = ['Должно быть число!']
        if not str(amount).isalnum():
            errors['amount'] = ['Должно быть число!']

        files = request.files
        img = files.get('image', None)

        if not img:
            if not goods_id:
                errors['image'] = ['Пожалуйста, прикрепите картику!']
        else:
            filename = secure_filename(img.filename)
            ext = filename.split('.')[-1]
            if ext not in ['png', 'jpg', 'jpeg']:
                errors['image'] = ['Пожалйста, загрузите файл jpg или png']

        if errors:
            db_sess = db_session.create_session()

            categories = db_sess.query(Category).all()
            char_types = db_sess.query(CharacteristicsType).all()

            goods = None
            if goods_id:
                goods = db_sess.query(Goods).get(goods_id)

            template = render_template('goods_edit_page.html',
                                       categories=categories,
                                       char_types=char_types,
                                       errors=errors,
                                       goods=goods)
            db_sess.close()
            return template

        db_sess = db_session.create_session()

        if bonus_points and str(bonus_points).isalnum():
            bonus_points = int(bonus_points)
        else:
            bonus_points = 0

        if goods_id:
            goods = db_sess.query(Goods).get(goods_id)
            goods.categories.clear()
            goods.characteristics.clear()
            goods.name = name
            goods.amount = int(amount)
            goods.price = int(price)

            if bonus_points:
                goods.gives_bonus_points = bonus_points
        else:
            goods = Goods(
                name=name,
                amount=int(amount),
                price=int(price),
                gives_bonus_points=bonus_points
            )

        data = {
            'categories': categ_items,
            'characteristics': char_items,
            'description': description
        }

        parse_goods_data(data, goods, db_sess)

        if img:
            filename = secure_filename(img.filename)
            ext = filename.split('.')[-1]

            new_fname = f'{uuid.uuid4()}.{ext}'
            img.save(f'static/img/goods/{new_fname}')
            goods.img_file_path = f'img/goods/{new_fname}'

        if not goods_id:
            db_sess.add(goods)

        db_sess.commit()
        db_sess.close()
        return redirect(url_for('all_goods_page'))


@app.route('/categories/<int:categ_id>')
def goods_in_category(categ_id):
    page = request.args.get('page', 1, type=int)

    db_sess = db_session.create_session()
    category = db_sess.query(Category).get(categ_id)
    categories = db_sess.query(Category).filter_by(parent_id=None)
    query = db_sess.query(Goods).join(Goods.categories).filter(Category.id == categ_id)
    goods = paginate(query, page, 6)

    if not category:
        db_sess.close()
        abort(404)

    template = render_template('goods_list_page.html',
                               title=f'Категория: {category.name}',
                               goods_items=goods,
                               category=category,
                               categories=categories)

    db_sess.close()
    return template


@login_required
@app.route('/goods/<int:goods_id>/delete')
def delete_goods(goods_id):
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

    db_sess = db_session.create_session()
    goods = db_sess.query(Goods).get(goods_id)
    db_sess.delete(goods)
    db_sess.commit()
    db_sess.close()

    return redirect(url_for('all_goods_page'))


@app.route('/goods/<int:goods_id>', methods=['GET', 'POST'])
def goods_one_page(goods_id):
    if request.method == 'POST':
        db_sess = db_session.create_session()
        if current_user.is_authenticated:
            title = request.form['review_title']
            content = request.form['review_content']
            rating = int(request.form['rating'])

            reviews = db_sess.query(Review).filter_by(user_id=current_user.id).first()
            if reviews:
                flash('Вы уже оставили отзыв на этот товар!', 'danger')
                return redirect(url_for('goods_one_page', goods_id=goods_id, reviews_page=1))

            review = Review(
                title=title,
                content=content,
                rating=rating,
                goods_id=goods_id,
                user_id=current_user.id
            )

            db_sess.add(review)
            db_sess.commit()
            db_sess.close()

            return redirect(url_for('goods_one_page', goods_id=goods_id, reviews_page=1, scroll_to_reviews='1'))
        else:
            return redirect(url_for('login', next=f'/goods/{goods_id}'))

    elif request.method == 'GET':
        db_sess = db_session.create_session()

        goods = db_sess.query(Goods).get(goods_id)

        if not goods:
            abort(404)

        reviews_page = request.args.get('reviews_page', 1, type=int)
        scroll_to_reviews = request.args.get('scroll_to_reviews', 1, type=int)
        from_category = request.args.get('from_category', 0, type=int)

        query = db_sess.query(Review).filter_by(goods_id=goods_id).order_by(desc(Review.created_date))
        reviews = paginate(query, reviews_page, 4)

        categories = db_sess.query(Category).filter_by(parent_id=None)
        if from_category > 0:
            category = db_sess.query(Category).get(from_category)
        else:
            from_category = goods.get_main_categ()

        template = render_template('goods_one_page.html', title='',
                                   reviews=reviews,
                                   goods=goods,
                                   time_format_func=ru_format_str_time,
                                   from_category=from_category,
                                   categories=categories)
        db_sess.close()
        return template
