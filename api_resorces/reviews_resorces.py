from flask_restful import reqparse, \
    abort, Resource
from flask import jsonify
from data import db_session
from data.goods import Goods
from data.users import User
from data.reviews import Review

from .api_login import token_required, check_user


class ReviewResource(Resource):
    def get(self, review_id):
        session = db_session.create_session()
        review = session.query(Review).get(review_id)

        if not review:
            abort(404, message=f'Goods with id: {review_id} not found')

        review_dict = review.to_dict(only=('title', 'content',
                                           'rating', 'created_date',
                                           'goods_id'))

        user_public_id = review.user.public_id
        review_dict['user_public_id'] = user_public_id

        return jsonify({'review': review_dict})

    @token_required
    def delete(self, current_user, review_id):
        session = db_session.create_session()
        review = session.query(Review).get(review_id)

        if not review:
            abort(404, message=f'Goods with id: {review_id} not found')

        check_user(current_user, review.user.public_id)

        session.delete(review)
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})

    @token_required
    def post(self, current_user, review_id):
        session = db_session.create_session()
        review = session.query(Review).get(review_id)

        check_user(current_user, review.user.public_id)

        parser = reqparse.RequestParser()
        parser.add_argument('title', required=False)
        parser.add_argument('content', required=False)
        parser.add_argument('rating', required=False, type=int)
        args = parser.parse_args()

        for key in args:
            if args[key] is not None:
                review.__setattr__(key, args[key])

        session.commit()
        session.close()

        return jsonify({'success': 'OK'})


class ReviewListResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('by_users', required=False, type=str, action='append')
        parser.add_argument('for_goods', required=False, type=int, action='append')
        parser.add_argument('amount', required=False, type=int)

        args = parser.parse_args()
        users, goods = args['by_users'], args['for_goods']

        amt = args.get('amount', None)
        if amt is None:
            amt = 1000

        session = db_session.create_session()
        reviews_all = session.query(Review).all()

        reviews, count = [], 0
        for review in reviews_all:
            if (not users) or review.user.public_id in users:
                if (not goods) or review.goods_id in goods:
                    reviews.append(review)
                    count += 1
                    if count >= amt:
                        break

        out_dicts = []
        for review in reviews:
            review_dict = review.to_dict(only=('title', 'content',
                                               'rating', 'created_date',
                                               'goods_id'))

            user_public_id = review.user.public_id
            review_dict['user_public_id'] = user_public_id
            out_dicts.append(review_dict)

        session.close()
        return jsonify({'reviews': out_dicts})

    @token_required
    def post(self, current_user):
        if not current_user or not current_user.is_admin:
            abort(401, message=f'You don\'t have enough rights to do that')

        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True)
        parser.add_argument('content', required=True)
        parser.add_argument('rating', required=True, type=int)
        parser.add_argument('for_goods', required=True, type=int)
        args = parser.parse_args()

        session = db_session.create_session()

        goods = session.query(Goods).get(args['for_goods'])

        review = Review(
            title=args['title'],
            content=args['content'],
            rating=args['rating'],
            goods=goods,
            user=current_user
        )

        session.add(review)
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})
