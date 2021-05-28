import sqlalchemy
from .db_session import SqlAlchemyBase


class Index(SqlAlchemyBase):
    __tablename__ = 'index'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    keyword = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    weight = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    goods_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
