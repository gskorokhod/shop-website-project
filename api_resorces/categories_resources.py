from flask_restful import reqparse, \
    abort, Resource
from flask import jsonify
from data import db_session
from data.goods import Category

from .api_login import token_required


class CategoriesResource(Resource):
    def get(self, categ_id):
        session = db_session.create_session()
        category = session.query(Category).get(categ_id)

        if not category:
            abort(404, message=f'Category with id: {categ_id} not found')

        session.close()
        return jsonify({'category': category.to_dict(only=('id', 'name'))})

    @token_required
    def delete(self, current_user, categ_id):
        if not current_user or not current_user.is_admin:
            abort(401, message=f'You don\'t have enough rights to do that')

        session = db_session.create_session()
        category = session.query(Category).get(categ_id)

        if not category:
            abort(404, message=f'Category with id: {categ_id} not found')

        session.delete(category)
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})


class CategoriesListResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('amount', required=False, type=int)
        parser.add_argument('primary', required=False, type=int)
        args = parser.parse_args()

        session = db_session.create_session()
        categories = list(session.query(Category).all())

        if args.get('primary', None) == 1:
            categories = [x for x in categories if not x.parent_id]

        session.close()

        return jsonify({'categories': [item.to_dict(
            only=('id', 'name')) for item in categories[:args.get('amount', 1000)]]})

    @token_required
    def post(self, current_user):
        if not current_user or not current_user.is_admin:
            abort(401, message=f'You don\'t have enough rights to do that')

        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('parent_id', required=False, type=int)
        args = parser.parse_args()

        session = db_session.create_session()

        category = Category(name=args['name'],
                            parent_id=args.get('parent_id', None))

        session.add(category)
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})
