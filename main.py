from flask import Flask
from flask_apscheduler import APScheduler
from data import db_session
from flask_login import LoginManager

from data.goods import Goods
from data.users import User
from flask_restful import Api

from search import search

from app import app, scheduler_daily_job

login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)

db_session.global_init("db/shop.db")

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

MAIN_DAILY_TASK_ID = 'MAIN_DAILY_TASK_ID'

from api_resorces import goods_resources, users_resources, \
    api_login, orders_resources, reviews_resorces, categories_resources, characteristics_resources

api.add_resource(goods_resources.GoodsListResource, '/api/v1/goods')
api.add_resource(goods_resources.GoodsResource, '/api/v1/goods/<int:goods_id>')
api.add_resource(users_resources.UsersListResource, '/api/v1/users')
api.add_resource(users_resources.UserResource, '/api/v1/users/<string:public_id>')
api.add_resource(orders_resources.OrdersListResource, '/api/v1/orders')
api.add_resource(orders_resources.OrderResource, '/api/v1/orders/<string:public_id>')
api.add_resource(reviews_resorces.ReviewListResource, '/api/v1/reviews')
api.add_resource(reviews_resorces.ReviewResource, '/api/v1/reviews/<int:review_id>')
api.add_resource(categories_resources.CategoriesListResource, '/api/v1/categories')
api.add_resource(categories_resources.CategoriesResource, '/api/v1/categories/<int:categ_id>')
api.add_resource(characteristics_resources.CharacteristicsTypeListResource, '/api/v1/characteristics')
api.add_resource(characteristics_resources.CharacteristicsTypeResource, '/api/v1/characteristics/<int:ch_id>')

scheduler.add_job(id=MAIN_DAILY_TASK_ID, func=scheduler_daily_job, trigger='cron', hour=0, minute=0, second=0)


@app.route('/api/v1/login')
def api_login_handle():
    return api_login.api_login()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    db_sess.close()
    return user


def index_all_goods():
    db_sess = db_session.create_session()
    goods = db_sess.query(Goods).all()
    for g in goods:
        search.index_goods(g)
    db_sess.close()


def main():
    index_all_goods()
    app.run()


if __name__ == '__main__':
    main()
