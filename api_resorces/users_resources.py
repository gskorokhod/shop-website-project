from flask_restful import reqparse, \
    abort, Resource
from flask import jsonify
from data import db_session
from data.users import User
from werkzeug.security import generate_password_hash, check_password_hash

from .api_login import token_required, check_user


def check_if_email_taken(email):
    session = db_session.create_session()
    users = session.query(User).filter_by(email=email).all()

    return bool(users)


def check_if_username_taken(username):
    session = db_session.create_session()
    users = session.query(User).filter_by(username=username).all()

    return bool(users)


def check_credentials(email, username):
    em = not check_if_email_taken(email)
    un = not check_if_username_taken(username)

    return em and un


class UserResource(Resource):
    def get(self, public_id):
        session = db_session.create_session()
        user = session.query(User).filter_by(public_id=public_id).first()

        if not user:
            abort(404, message=f'User with id: {public_id} not found')

        user_dict = user.to_dict(only=('username', 'first_name',
                                       'last_name', 'email', 'phone',
                                       'is_admin', 'created_date', 'public_id'))

        session.close()

        return jsonify({'user': user_dict})

    @token_required
    def delete(self, current_user, public_id):
        check_user(current_user, public_id)

        session = db_session.create_session()
        user = session.query(User).filter_by(public_id=public_id).first()

        if not user:
            abort(404, message=f'User with id: {public_id} not found')

        session.delete(user)
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})

    @token_required
    def put(self, current_user, public_id):
        if not current_user or not current_user.is_admin:
            abort(401, message=f'You don\'t have enough rights to do that')

        parser = reqparse.RequestParser()
        parser.add_argument('promote', required=True, type=str)
        args = parser.parse_args()

        session = db_session.create_session()
        user = session.query(User).filter_by(public_id=public_id).first()

        if not user:
            abort(404, message=f'User with id: {public_id} not found')

        do_promote = str(args['promote']).lower() in ('1', 'true')

        user.is_admin = do_promote
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    @token_required
    def get(self, current_user):
        if not current_user or not current_user.is_admin:
            abort(401, message=f'You don\'t have enough rights to do that')

        parser = reqparse.RequestParser()
        parser.add_argument('amount', required=False, type=int)

        args = parser.parse_args()

        session = db_session.create_session()
        users = list(session.query(User).all())

        session.close()

        return jsonify({'users': [item.to_dict(
            only=('username', 'first_name',
                  'last_name', 'email', 'phone',
                  'is_admin', 'created_date', 'public_id'))
            for item in users[:args.get('amount', 1000)]]})

    @token_required
    def post(self, current_user):
        if not current_user or not current_user.is_admin:
            abort(401, message=f'You don\'t have enough rights to do that')

        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True)
        parser.add_argument('first_name', required=False)
        parser.add_argument('last_name', required=False)
        parser.add_argument('email', required=True)
        parser.add_argument('phone', required=False)
        parser.add_argument('password', required=True)

        args = parser.parse_args()
        session = db_session.create_session()

        if not check_credentials(args['email'], args['username']):
            abort(403, message=f'This email or username is already taken')

        user = User(
            username=args['username'],
            email=args['email'],
            hashed_password=generate_password_hash(args['password'], method='sha256')
        )

        user.phone = args.get('phone', None)
        user.first_name = args.get('first_name', None)
        user.last_name = args.get('last_name', None)

        session.add(user)
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})
