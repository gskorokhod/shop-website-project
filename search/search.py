from sqlalchemy import desc

from .text_analyze import tokenize
from .search_data import db_session
from .search_data.index import Index

DESC_OCCURENCE_WEIGHT = 1
TITLE_OCCURENCE_WEIGHT = 10


db_session.global_init("db/search.db")


def index_goods(goods):
    db_sess = db_session.create_session()

    name, desc = goods.name, goods.description
    title_tokens = tokenize(name)
    desc_tokens = tokenize(desc)

    for token in title_tokens:
        existing_entry = db_sess.query(Index).filter_by(keyword=token).filter_by(goods_id=goods.id).first()
        if existing_entry:
            existing_entry.weight += TITLE_OCCURENCE_WEIGHT
        else:
            new_entry = Index(keyword=token, weight=TITLE_OCCURENCE_WEIGHT, goods_id=goods.id)
            db_sess.add(new_entry)

    for token in desc_tokens:
        existing_entry = db_sess.query(Index).filter_by(keyword=token).filter_by(goods_id=goods.id).first()
        if existing_entry:
            existing_entry.weight += DESC_OCCURENCE_WEIGHT
        else:
            new_entry = Index(keyword=token, weight=DESC_OCCURENCE_WEIGHT, goods_id=goods.id)
            db_sess.add(new_entry)

    db_sess.commit()
    db_sess.close()


def get_ids_by_keyword(kw):
    db_sess = db_session.create_session()
    entries = set([x.id for x in db_sess.query(Index).filter_by(keyword=kw)])
    db_sess.close()
    return entries


def get_ids_by_keywords(kw_list):
    if kw_list:
        res = get_ids_by_keyword(kw_list[0])
        for kw in kw_list[1:]:
            res = res.intersection(get_ids_by_keyword(kw))
        return res
    else:
        return {}


def get_by_kw(kw_list):
    db_sess = db_session.create_session()
    ids = get_ids_by_keywords(kw_list)
    items = [db_sess.query(Index).get(x_id) for x_id in ids]
    tuples = [(x.goods_id, x.weight) for x in items]
    tuples.sort(key=lambda x: x[1])
    return tuples


def get_by_query(query):
    q_tokens = tokenize(query)
    return get_by_kw(q_tokens)
