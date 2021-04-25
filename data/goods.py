import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm import backref
from sqlalchemy_serializer import SerializerMixin

from .misc import Rating
from .db_session import SqlAlchemyBase

goods_to_category = sqlalchemy.Table(
    'goods_to_category',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('goods', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('goods.id')),
    sqlalchemy.Column('categories', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('categories.id'))
)

goods_to_characteristics = sqlalchemy.Table(
    'goods_to_characteristics',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('goods', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('goods.id')),
    sqlalchemy.Column('characteristics', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('characteristics.id'))
)


class CharacteristicsType(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'characteristics_types'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)


class Characteristics(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'characteristics'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    type_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("characteristics_types.id"))

    type = orm.relation('CharacteristicsType')

    value = sqlalchemy.Column(sqlalchemy.String)


class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'categories'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    parent_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey('categories.id'))

    children = orm.relation("Category",
                            backref=backref('parent', remote_side=[id]))

    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)


class Goods(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'goods'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    img_file_path = sqlalchemy.Column(sqlalchemy.String, nullable=False,
                                      default='img/goods/no_image.jpg')

    amount = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)

    price = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)

    gives_bonus_points = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)

    categories = orm.relation('Category',
                              secondary='goods_to_category',
                              backref='goods')

    characteristics = orm.relation('Characteristics',
                                   secondary='goods_to_characteristics',
                                   backref='goods')

    reviews = orm.relation('Review', back_populates='goods')

    def get_rating(self):
        return Rating([x.rating for x in self.reviews])

    def get_main_categ(self):
        primary_categories = [x for x in self.categories if not x.parent_id]
        if primary_categories:
            return primary_categories[0]
        else:
            if self.categories:
                return self.categories[0]
            else:
                return None
