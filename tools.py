from flask import abort
from flask_sqlalchemy import Pagination

from data import db_session
from data.goods import Goods
from data.orders import OrderElement

import datetime


MONTH_NAMES_RU = ['', 'Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня',
                  'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря']


def paginate(query, page, per_page=20, error_out=True):
    if error_out and page < 1:
        abort(404)

    items = query.limit(per_page).offset((page - 1) * per_page).all()

    if not items and page != 1 and error_out:
        abort(404)

    # No need to count if we're on the first page and there are fewer
    # items than we expected.
    if page == 1 and len(items) < per_page:
        total = len(items)
    else:
        total = query.order_by(None).count()

    return Pagination(query, page, per_page, total, items)


def ru_format_str_time(time: datetime.datetime, show_exact_time=True):
    s_month = MONTH_NAMES_RU[time.month]
    s_date = f'{time.day} {s_month} {time.year}'

    if show_exact_time:
        s_time = f', {time.hour}:{time.minute}'
    else:
        s_time = ''

    return s_date + s_time


def get_orders_containing_goods(session, goods):
    goods_id = goods.id
    ans = []

    order_elems = session.query(OrderElement).filter_by(goods_id=goods_id)
    for el in order_elems:
        order = el.order
        if order.status and order.status.name.lower() != 'order_closed':
            ans.append(order)

    return ans
