from flask_restful import reqparse, \
    abort, Resource
from flask import jsonify
from data import db_session
from data.goods import CharacteristicsType

from .api_login import token_required


class CharacteristicsTypeResource(Resource):
    def get(self, ch_id):
        session = db_session.create_session()
        characteristic = session.query(CharacteristicsType).get(ch_id)

        if not characteristic:
            abort(404, message=f'Characteristic with id: {ch_id} not found')

        session.close()

        return jsonify({'characteristic_type': characteristic.to_dict(only=('id', 'name'))})

    @token_required
    def delete(self, current_user, ch_id):
        if not current_user or not current_user.is_admin:
            abort(401, message=f'You don\'t have enough rights to do that')

        session = db_session.create_session()
        characteristic = session.query(CharacteristicsType).get(ch_id)

        if not characteristic:
            abort(404, message=f'Characteristic with id: {ch_id} not found')

        session.delete(characteristic)
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})


class CharacteristicsTypeListResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('amount', required=False, type=int)
        args = parser.parse_args()

        session = db_session.create_session()
        characteristics = list(session.query(CharacteristicsType).all())[:args.get('amount', 1000)]
        session.close()

        return jsonify({'characteristics': [item.to_dict(
            only=('id', 'name')) for item in characteristics]})

    @token_required
    def post(self, current_user):
        if not current_user or not current_user.is_admin:
            abort(401, message=f'You don\'t have enough rights to do that')

        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        args = parser.parse_args()

        session = db_session.create_session()

        category = CharacteristicsType(name=args['name'])

        session.add(category)
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})
