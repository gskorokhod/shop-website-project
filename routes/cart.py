from flask import request, render_template, abort, session, jsonify

from data import db_session
from main import app

from data.goods import Goods


@app.route('/cart')
def cart_page():
    db_sess = db_session.create_session()

    cart_items = []
    price = amt = 0
    if 'cart' in session.keys():
        for item in session['cart']:
            goods = db_sess.query(Goods).get(item['goods_id'])
            cart_item = {
                'goods': goods,
                'amount': item['amount']
            }

            amt += item['amount']
            price += goods.price * item['amount']

            cart_items.append(cart_item)

    template = render_template('cart_page.html',
                               title='Корзина',
                               cart_items=cart_items,
                               price=price,
                               amount=amt)

    db_sess.close()
    return template


@app.route('/api/v1/cart', methods=['POST', 'GET', 'DELETE'])
def cart_list_api():
    if request.method == 'GET':
        db_sess = db_session.create_session()

        out = {'total': 0, 'amount': 0}

        if 'cart' in session.keys():
            out['items'] = []

            amt, total = 0, 0
            for item in session['cart']:
                goods = db_sess.query(Goods).get(item['goods_id'])
                if goods:
                    out['items'].append(item)
                    amt += item['amount']
                    total += int(goods.price * item['amount'])

            out['total'] = total
            out['amount'] = amt

        db_sess.close()
        return jsonify({'cart': out}), 200
    elif request.method == 'POST':
        form = request.form

        goods_id, amount = int(form['goods_id']), int(form['amount'])
        cart_obj = {
            'goods_id': goods_id,
            'amount': amount
        }

        if 'cart' in session.keys():
            flag = True
            for item in session['cart']:
                if item['goods_id'] == goods_id:
                    item['amount'] += amount
                    flag = False
                    break

            if flag:
                session['cart'].append(cart_obj)
        else:
            session['cart'] = [cart_obj]

        session.modified = True
        print(session['cart'])
        return jsonify({'success': 'OK', 'cart': session['cart']}), 200
    elif request.method == 'DELETE':
        session['cart'] = []
        session.modified = True
        return jsonify({'success': 'OK', 'cart': session['cart']}), 200


@app.route('/api/v1/cart/<int:item>', methods=['GET', 'POST', 'DELETE'])
def cart_one_api(item):
    if 'cart' in session.keys():
        item_ind = int(item)

        if item_ind not in range(0, len(session['cart'])):
            abort(404)

        if request.method == 'POST':
            amt = int(request.args.get('amount'))
            if amt > 0:
                session['cart'][item_ind]['amount'] = amt
                session.modified = True
                return jsonify({'success': 'OK'})
            abort(401)
        elif request.method == 'GET':
            return jsonify({'cart_item': session['cart'][item_ind]})
        elif request.method == 'DELETE':
            del session['cart'][item_ind]
            session.modified = True
            return jsonify({'success': 'OK'})
