import pymongo
import db.db_base as db


def query_new_news(user_id):
    user_id = int(user_id)
    news_table = db.get_db().yanfuNewsDB.newsTable
    history_table = db.get_db().yanfuNewsDB.historyTable

    condition = {'user_id': user_id}
    history = history_table.find(condition)
    history_list = list()

    for a_history in history:
        history_list.append(a_history['news_id'])

    print(history_list)

    condition = {'_id': {'$nin': history_list}}  # 剔除看过的新闻
    field = {
        'content': 0,
        'url': 0,
        'title_hash': 0,
        'content_hash': 0,
    }  # 过滤不需要的字段，减少内存占用

    data = news_table.find(condition, field).sort('time', pymongo.DESCENDING)
    data = list(data)
    return data
