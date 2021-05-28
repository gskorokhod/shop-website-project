from flask import Flask
from data import db_session
from data.goods import Goods
from tools import get_orders_containing_goods


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

from routes import home, goods, users, cart, orders


def cleanup_deleted_goods():
    db_sess = db_session.create_session()
    all_goods = db_sess.query(Goods).all()

    for item in all_goods:
        if not get_orders_containing_goods(db_sess, goods):
            db_sess.delete(item)

    db_sess.commit()
    db_sess.close()


def scheduler_daily_job():
    cleanup_deleted_goods()
