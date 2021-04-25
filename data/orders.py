import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from .misc import generate_uuid


class Status(SqlAlchemyBase):
    __tablename__ = 'order_statuses'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    full_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)


class OrderElement(SqlAlchemyBase):
    __tablename__ = 'order_elements'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    order_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("orders.id"), nullable=False)

    goods_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("goods.id"), nullable=False)

    order = orm.relation('Order')
    goods = orm.relation('Goods')

    amount = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=1)


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    public_id = sqlalchemy.Column(sqlalchemy.String(50),
                                  unique=True,
                                  nullable=False,
                                  default=generate_uuid)

    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    update_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    delivery_date = sqlalchemy.Column(sqlalchemy.DateTime)

    elements = orm.relation('OrderElement', back_populates='order')

    location_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("locations.id"))

    location = orm.relation('Location')

    status_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey("order_statuses.id"))

    status = orm.relation('Status')

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"), nullable=True)

    user = orm.relation('User', back_populates='orders')
