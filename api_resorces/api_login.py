from functools import wraps

from flask import jsonify, request, make_response, abort
from data import db_session
from data.users import User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from app import app


def api_login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401)

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(username=auth.username).first()

    if not user:
        return make_response('User not found', 401)

    if check_password_hash(user.hashed_password, auth.password):
        token_data = {
            'public_id': user.public_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }
        token = jwt.encode(token_data, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    else:
        return make_response('Incorrect password', 401)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return make_response(jsonify({'message': 'Token is missing!'}), 401)

        db_sess = db_session.create_session()
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            public_id = data['public_id']

            current_user = db_sess.query(User).filter_by(public_id=public_id).first()
        except Exception as error:
            e = error
            print(e.__class__.__name__)
            return make_response(jsonify({'message': 'Token is invalid!'}), 401)

        db_sess.close()
        return f(*args, current_user, **kwargs)

    return decorated


def check_user(current_user, public_id):
    if not current_user:
        abort(401, message=f'Authentication error')
    if not (current_user.public_id == public_id or current_user.is_admin):
        abort(401, message=f'You don\'t have enough rights to do that')