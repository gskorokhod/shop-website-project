import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .misc import generate_uuid

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    public_id = sqlalchemy.Column(sqlalchemy.String(50),
                                  unique=True,
                                  nullable=False,
                                  default=generate_uuid)

    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)

    first_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    last_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    profile_pic_path = sqlalchemy.Column(sqlalchemy.String, nullable=False,
                                         default='img/user_pics/default_user.png')

    username = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=False)
    phone = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    bonus_points = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)

    reviews = orm.relation("Review", back_populates='user')

    orders = orm.relation("Order", back_populates='user')

    location_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("locations.id"))

    address = orm.relation('Location')
