import pymongo

from flask import g

# 与数据库建立连接，在db包中共用连接
def get_db():
    if 'db' not in g:
        g.db = pymongo.MongoClient('127.0.0.1', 27017)
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
