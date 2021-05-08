from flask import request, render_template, abort, session, redirect, url_for, flash

from data import db_session
from data.locations import Location
from app import app

from forms.orders_forms import OrderForm

from data.goods import Goods
from data.orders import Order, Status, OrderElement
from flask_login import current_user, login_required

from tools import paginate, ru_format_str_time


@app.route('/orders/track')
def orders_track():
    form_id = request.args.get('public_id', None, type=str)
    if form_id:
        return redirect(url_for('orders_track_page', public_id=form_id))

    return render_template('orders_track_page.html')


@app.route('/orders/track/<string:public_id>')
def orders_track_page(public_id):
    form_id = request.args.get('public_id', None, type=str)
    if form_id:
        return redirect(url_for('orders_track_page', public_id=form_id))

    db_sess = db_session.create_session()
    order = db_sess.query(Order).filter_by(public_id=public_id).first()

    if order:
        if order.user:
            if not current_user.is_authenticated:
                db_sess.close()
                abort(403)
            elif order.user != current_user:
                db_sess.close()
                abort(403)

        template = render_template('orders_one_page.html',
                                   title='Заказ',
                                   order=order,
                                   time_format_func=ru_format_str_time)

        db_sess.close()
        return template
    else:
        db_sess.close()
        abort(404)


@app.route('/orders')
@login_required
def orders_list_page():
    page = request.args.get('page', 1, type=int)

    db_sess = db_session.create_session()

    if current_user.is_admin:
        query = db_sess.query(Order)
    else:
        query = db_sess.query(Order).filter_by(user_id=current_user.id)

    orders = paginate(query, page, 6)
    template = render_template('orders_page.html',
                               title='Заказы',
                               orders=orders,
                               time_format_func=ru_format_str_time)
    db_sess.close()
    return template


@app.route('/checkout', methods=['GET', 'POST'])
def checkout_page():
    order_form = OrderForm()

    if order_form.validate_on_submit():
        db_sess = db_session.create_session()

        location = Location(
            country=order_form.country.data,
            city=order_form.city.data,
            street=order_form.street.data,
            building=order_form.building.data,
            entrance=order_form.entrance.data,
            floor=order_form.floor.data,
            flat=order_form.flat.data
        )

        status = db_sess.query(Status).filter_by(name='processing').first()
        if not status:
            status = Status(name='processing',
                            full_name='Заказ принят',
                            description='Мы приняли Ваш заказ. Сейчас он находится в обработке.')

        description = order_form.description.data
        if not description:
            description = 'Нет описания'

        if current_user.is_authenticated:
            user = current_user
        else:
            user = None

        date = order_form.delivery_date.data

        order = Order(
            description=description,
            location=location,
            status_id=status.id,
            user=user,
            delivery_date=date
        )

        for item in session['cart']:
            goods = db_sess.query(Goods).get(item['goods_id'])
            amount = item['amount']

            elem = OrderElement(
                order=order,
                goods_id=item['goods_id'],
                amount=item['amount']
            )

            goods.amount -= amount
            order.elements.append(elem)

        db_sess.add(order)
        db_sess.commit()

        order_uuid = order.public_id
        if not current_user.is_authenticated:
            flash('''Вы не зарегистрированы, поэтому для отслеживания заказа вам понадобится его уникальный ID.
                  Сохраните его!''', 'danger')
        db_sess.close()

        return redirect(url_for('orders_track_page', public_id=order_uuid))
    else:
        db_sess = db_session.create_session()

        cart_items = []
        price = 0
        if 'cart' in session.keys():
            for item in session['cart']:
                goods = db_sess.query(Goods).get(item['goods_id'])

                cart_item = {
                    'goods': goods,
                    'amount': item['amount']
                }

                price += goods.price * item['amount']
                cart_items.append(cart_item)

        template = render_template('checkout page.html',
                                   title='Оформить заказ',
                                   form=order_form,
                                   price=price,
                                   cart_items=cart_items)

        db_sess.close()
        return template
