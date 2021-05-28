from flask import request, render_template
from flask_login import current_user
from sqlalchemy import desc

from data.goods import Goods, Category
from tools import paginate
from data import db_session
from app import app


@app.route('/')
@app.route('/home')
def index_page():
    page = request.args.get('page', 1, type=int)

    db_sess = db_session.create_session()

    query = db_sess.query(Goods)
    if not (current_user.is_authenticated and current_user.is_admin):
        query = query.filter_by(is_visible=True)

    query = query.order_by(desc(Goods.times_bought))

    popular_goods = paginate(query, page, 6)
    categories = db_sess.query(Category).filter_by(parent_id=None)
    db_sess.close()

    return render_template('main_page.html',
                           title='Главная',
                           popular_goods=popular_goods,
                           categories=categories)
