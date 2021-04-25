from main import app, db_session
from data.goods import Category
from data.orders import Status
from data.users import User
from data.goods import Goods
from werkzeug.security import generate_password_hash

db_session.global_init("db/shop.db")
session = db_session.create_session()

default_user = User(
            username='admin',
            email='admin@test.com',
            hashed_password=generate_password_hash('admin', method='sha256'),
            is_admin=True
        )

session.add(default_user)

session.commit()
session.close()
