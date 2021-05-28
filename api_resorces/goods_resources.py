from flask_restful import reqparse, \
    abort, Resource
from flask import jsonify
from data import db_session
from data.goods import Goods, Category, Characteristics, CharacteristicsType

from .api_login import token_required


def parse_categories(args, goods, session):
    all_categs = []
    if args.get('categories', None) is not None:
        for categ_id in args['categories']:
            categ_id = int(categ_id)

            if categ_id not in all_categs:
                category = session.query(Category).filter_by(id=categ_id).first()

                if not category:
                    abort(404)

                all_categs.append(categ_id)
                goods.categories.append(category)


def parse_characteristics(args, goods, session):
    all_chars = []
    if args.get('characteristics', None) is not None:
        for ch_item in args['characteristics']:
            ch_id, ch_value, ch_name = str(ch_item).split('#')

            if ch_id.lower() == 'null':
                new_ch_type = CharacteristicsType(name=ch_name)
                session.add(new_ch_type)
                session.commit()
                ch_id = new_ch_type.id
            else:
                ch_id = int(ch_id)

            if ch_id not in all_chars:
                ch_type = session.query(CharacteristicsType).get(ch_id)
                if not ch_type:
                    abort(404)

                all_chars.append(ch_type)
                characteristic = Characteristics(type=ch_type, value=ch_value)

                goods.characteristics.append(characteristic)


def parse_goods_data(args, goods, session):
    parse_categories(args, goods, session)
    parse_characteristics(args, goods, session)

    description = args.get('description', None)
    if description is None:
        description = 'No description provided'
    goods.description = description


class GoodsResource(Resource):
    def get(self, goods_id):
        session = db_session.create_session()
        goods = session.query(Goods).get(goods_id)

        if not goods:
            abort(404, message=f'Goods with id: {goods_id} not found')

        goods_dict = goods.to_dict(only=('name', 'description',
                                         'amount', 'price', 'id'))

        categories = [category.name for category in goods.categories]
        characteristics = [(ch.type.name, ch.value) for ch in goods.characteristics]
        ratings = [int(rev.rating) for rev in goods.reviews]

        avg_rating = 0
        if ratings:
            avg_rating = sum(ratings) / len(ratings)

        goods_dict['categories'] = categories
        goods_dict['characteristics'] = characteristics
        goods_dict['rating'] = avg_rating

        session.close()

        return jsonify({'goods': goods_dict})

    @token_required
    def delete(self, current_user, goods_id):
        if not current_user or not current_user.is_admin:
            abort(401, message=f'You don\'t have enough rights to do that')

        session = db_session.create_session()
        goods = session.query(Goods).get(goods_id)

        if not goods:
            abort(404, message=f'Goods with id: {goods_id} not found')

        session.delete(goods)
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})

    @token_required
    def post(self, current_user, goods_id):
        if not current_user or not current_user.is_admin:
            abort(401, message=f'You don\'t have enough rights to do that')

        parser = reqparse.RequestParser()
        parser.add_argument('name', required=False)
        parser.add_argument('description', required=False)
        parser.add_argument('amount', required=False, type=int)
        parser.add_argument('price', required=False, type=int)
        parser.add_argument('gives_bonus_points', required=False)
        parser.add_argument('categories', required=False, action='append', type=int)
        parser.add_argument('characteristics', required=False, action='append', type=str)
        parser.add_argument('img_file_path', required=False, type=str)

        args = parser.parse_args()

        session = db_session.create_session()

        goods = session.query(Goods).get(goods_id)

        for key in args:
            if key not in ['categories', 'characteristics', 'description']:
                if args[key] is not None:
                    goods.__setattr__(key, args[key])

        parse_goods_data(args, goods, session)

        session.commit()
        session.close()

        return jsonify({'success': 'OK'})


class GoodsListResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('category', required=False)
        parser.add_argument('amount', required=False, type=int)

        args = parser.parse_args()
        category = args.get('category', None)

        session = db_session.create_session()
        goods = list(session.query(Goods).all())

        if category is None:
            g = goods
        else:
            g = [item for item in goods
                 if any([x.name == category for x in item.categories])]

        session.close()
        return jsonify({'goods': [item.to_dict(
            only=('name', 'description',
                  'amount', 'price', 'id', 'gives_bonus_points')) for item in g[:args.get('amount', 1000)]]})

    @token_required
    def post(self, current_user):
        if not current_user or not current_user.is_admin:
            abort(401, message=f'You don\'t have enough rights to do that')

        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, type=str)
        parser.add_argument('description', required=False, type=str)
        parser.add_argument('amount', required=True, type=int, default=0)
        parser.add_argument('price', required=True, type=int)
        parser.add_argument('gives_bonus_points', required=False, type=int, default=0)
        parser.add_argument('categories', required=False, action='append', type=int)
        parser.add_argument('characteristics', required=False, action='append', type=str)
        parser.add_argument('img_file_path', required=False, type=str)

        args = parser.parse_args()
        session = db_session.create_session()

        goods = Goods(
            name=args['name'],
            amount=args['amount'],
            price=args['price'],
            gives_bonus_points=args.get('gives_bonus_points', 0)
        )

        parse_goods_data(args, goods, session)

        session.add(goods)
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})
