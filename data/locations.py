import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Location(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'locations'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    country = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    street = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    building = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    entrance = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    floor = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    flat = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
