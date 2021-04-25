from datetime import datetime

from flask_restful import reqparse, \
    abort, Resource
from flask import jsonify, make_response
from data import db_session
from data.orders import Order, Status, OrderElement
from data.locations import Location
from data.users import User
from data.goods import Goods

from .api_login import token_required, check_user


def parser_add_location(parser):
    parser.add_argument('location_country', required=False, type=str)
    parser.add_argument('location_city', required=False, type=str)
    parser.add_argument('location_street', required=False, type=str)
    parser.add_argument('location_building', required=False, type=str)
    parser.add_argument('location_entrance', required=False, type=int)
    parser.add_argument('location_floor', required=False, type=int)
    parser.add_argument('location_flat', required=False, type=int)


def parse_location(d_args):
    location = Location(
        country=d_args.get('location_country', None),
        city=d_args.get('location_city', None),
        street=d_args.get('location_street', None),
        building=d_args.get('location_building', None),
        entrance=d_args.get('location_entrance', None),
        floor=d_args.get('location_floor', None),
        flat=d_args.get('location_flat', None)
    )
    return location


def parse_items(session, items_str, order):
    if items_str:
        for entry in items_str:
            goods_id, amt, *_ = str(entry).split('#')

            try:
                amt, goods_id = int(amt), int(goods_id)

                goods = session.query(Goods).get(goods_id)

                if goods:
                    if goods.amount - amt < 0:
                        abort(400, message='Not enough goods in storage!')

                    element = OrderElement(
                        order=order,
                        goods=goods,
                        amount=amt
                    )

                    goods.amount -= amt

                    order.elements.append(element)
            except ValueError:
                abort(400, message='Bad request format. Use <goods id>#<amount>')


def orders_validate_user(current_user, req_args):
    if not current_user:
        abort(401, message=f'You don\'t have enough rights to do that')
    elif not current_user.is_admin:
        user_uuid = req_args.get('by_user_public_id', None)
        if user_uuid:
            if not user_uuid == current_user.public_id:
                abort(401, message=f'You don\'t have enough rights to do that')
        else:
            req_args['by_user_public_id'] = current_user.public_id


class OrderResource(Resource):
    def get(self, public_id):
        session = db_session.create_session()
        order = session.query(Order).filter_by(public_id=public_id).first()

        if not order:
            abort(404, message=f'Order with id: {public_id} not found')

        order_dict = order.to_dict(only=('public_id', 'description',
                                         'created_date', 'delivery_date'))

        order_goods = []
        total_price = total_amount = total_bonus = 0
        for element in order.elements:
            goods = element.goods
            amount = element.amount
            order_goods.append({
                'name': goods.name,
                'id': goods.id,
                'amount': amount
            })

            total_price += goods.price * amount
            total_amount += amount
            total_bonus += goods.gives_bonus_points

        total = {
            'total_price': total_price,
            'total_bonus': total_bonus,
            'total_amount': total_amount
        }

        location = order.location.to_dict(only=(
            'country', 'city', 'street', 'building',
            'entrance', 'floor', 'flat'
        ))

        order_dict['goods'] = order_goods
        order_dict['total'] = total
        order_dict['location'] = location

        session.close()

        return jsonify({'goods': order_dict})

    @token_required
    def delete(self, current_user, public_id):
        session = db_session.create_session()
        order = session.query(Order).filter_by(public_id=public_id).first()

        if not order:
            abort(404, message=f'Order with id: {public_id} not found')

        check_user(current_user, order.user.public_id)

        session.delete(order.location)

        for el in order.elements:
            el.goods.amount += el.amount
            session.delete(el)
        order.elements.clear()

        session.delete(order)
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})

    @token_required
    def post(self, current_user, public_id):
        session = db_session.create_session()
        order = session.query(Order).filter_by(public_id=public_id).first()

        if not order:
            abort(404, message=f'Order with id: {public_id} not found')

        check_user(current_user, order.user.public_id)

        parser = reqparse.RequestParser()
        parser.add_argument('by_user_public_id', required=False, type=str)
        parser.add_argument('description', required=False, type=str)
        parser.add_argument('items', required=False, action='append', type=str)

        # Location data
        parser_add_location(parser)
        # --------------

        args = parser.parse_args()

        orders_validate_user(current_user, args)

        status = session.query(Status).filter_by(name='processing').first()
        if not status:
            status = Status(name='processing',
                            description='Мы приняли Ваш заказ. Сейчас он находится в обработке.')

        session.delete(order.location)

        for el in order.elements:
            el.goods.amount += el.amount
            session.delete(el)
        order.elements.clear()

        description = args.get('description', None)
        if description is None:
            description = ''
        order.description = description

        order.location = parse_location(args)
        order.status = status

        items_str = args.get('items', None)
        parse_items(session, items_str, order)

        session.commit()
        session.close()
        return jsonify({'success': 'OK'})

    @token_required
    def put(self, current_user, public_id):
        session = db_session.create_session()
        order = session.query(Order).filter_by(public_id=public_id).first()

        if not order:
            abort(404, message=f'Order with id: {public_id} not found')

        check_user(current_user, order.user.public_id)

        parser = reqparse.RequestParser()

        parser.add_argument('goods_id', type=int)
        parser.add_argument('action', type=str)
        parser.add_argument('amount', type=int)

        # Location data
        parser_add_location(parser)
        # --------------

        args = parser.parse_args()

        action = str(args['action']).lower()

        goods_id = args.get('goods_id', None)
        amount = args.get('amount', None)

        if goods_id is None:
            abort(404, message=f'Goods with id: {goods_id} not found')

        if action == 'update_goods':
            flag = True
            for el in order.elements:
                if el.goods.id == goods_id:
                    if amount is not None:
                        el.goods.amount += el.amount

                        if amount <= 0:
                            order.elements.remove(el)
                            session.delete(el)
                        else:
                            if el.goods.amount - amount < 0:
                                abort(400, message='Not enough goods in storage!')

                            el.goods.amount -= amount
                            el.amount = amount

                        flag = False
                        break
                    else:
                        abort(400, message='Bad request, check amount value')

            if flag:
                goods = session.query(Goods).get(goods_id)
                if goods and amount and amount > 0:
                    element = OrderElement(
                        order=order,
                        goods=goods,
                        amount=amount
                    )
                    order.elements.append(element)
        elif action == 'remove':
            for el in order.elements:
                if el.goods.id == goods_id:
                    order.elements.remove(el)
                    session.delete(el)
                    break
        elif action == 'update_location':
            session.delete(order.location)
            session.commit()

            location = parse_location(args)
            order.location = location
        else:
            msg = {
                'message': 'Invalid action parameter!',
                'available_actions': {
                    'update_goods': 'updates goods amount in order, removes them from order if new amount <= 0',
                    'remove': 'removes goods from order (parameter "amount" is ignored)',
                    'update_location': 'updates location'
                }
            }
            return make_response(jsonify(msg), 400)

        order.update_date = datetime.utcnow()
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})


class OrdersListResource(Resource):
    @token_required
    def get(self, current_user):
        parser = reqparse.RequestParser()
        parser.add_argument('amount', required=False, type=int)
        parser.add_argument('by_user_public_id', required=False, type=str)
        args = parser.parse_args()

        orders_validate_user(current_user, args)

        if str(args['by_user_public_id']).lower() == 'self':
            args['by_user_public_id'] = current_user.public_id

        session = db_session.create_session()
        by_user_public_id = args.get('by_user_public_id', None)

        if by_user_public_id is None:
            orders = list(session.query(Order).all())[:args.get('amount', 1000)]
        else:
            user = session.query(User).filter_by(public_id=by_user_public_id).first()
            orders_query = session.query(Order).filter(Order.user == user)
            orders = list(orders_query)[:args.get('amount', 1000)]

        output = []
        for item in orders:
            item_dict = item.to_dict(only=('public_id',
                                           'created_date',
                                           'delivery_date',
                                           'update_date'))

            if item.user:
                item_dict['user_public_id'] = item.user.public_id
            else:
                item_dict['user_public_id'] = None
            output.append(item_dict)

        return jsonify({'orders': output})

    @token_required
    def post(self, current_user):
        parser = reqparse.RequestParser()
        parser.add_argument('by_user_public_id', required=False, type=str)
        parser.add_argument('description', required=False, type=str)
        parser.add_argument('items', required=False, action='append', type=str)

        # Location data
        parser_add_location(parser)
        # --------------

        args = parser.parse_args()

        orders_validate_user(current_user, args)

        if str(args['by_user_public_id']).lower() == 'self':
            args['by_user_public_id'] = current_user.public_id

        by_user_public_id = args.get('by_user_public_id', None)
        session = db_session.create_session()

        location = parse_location(args)

        status = session.query(Status).filter_by(name='processing').first()
        if not status:
            status = Status(name='processing',
                            description='Мы приняли Ваш заказ. Сейчас он находится в обработке.')

        description = args.get('description', None)
        if description is None:
            description = ''

        order = Order(
            description=description,
            location=location,
            status=status
        )

        if by_user_public_id:
            user = session.query(User).filter_by(public_id=by_user_public_id).first()
            if user:
                order.user = user

        items_str = args.get('items', None)
        parse_items(session, items_str, order)

        session.add(order)
        session.commit()
        session.close()

        return jsonify({'success': 'OK'})
