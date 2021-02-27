import db.db_base as db
import pymongo
from datetime import datetime

field = {
    'content': 0,
    'url': 0,
    'title_hash': 0,
    'content_hash': 0,
}  # 过滤不需要的字段，减少内存占用


def query_one(news_id):
    news_id = int(news_id)
    table = db.get_db().yanfuNewsDB.newsTable
    condition = {'_id': news_id}
    data = table.find_one(condition)
    return data


def update_one_tags(news_id, static_tags, tags):
    news_id = int(news_id)
    table = db.get_db().yanfuNewsDB.newsTable
    condition = {'_id': news_id}
    update = {'$set': {
        'tags': tags,
        'static_tags': static_tags
    }}
    table.update_one(condition, update)


def update_one_info(news_id, author, category, stock):
    news_id = int(news_id)
    table = db.get_db().yanfuNewsDB.newsTable
    condition = {'_id': news_id}
    update = {'$set': {
        'author': author,
        'category': category,
        'stock': stock,
    }}
    table.update_one(condition, update)


# 查询数据库中共有多少条数据
def query_size():
    table = db.get_db().yanfuNewsDB.newsTable
    count = table.find().count()
    return count


# 按入库顺序查询所有新闻
def query_all(skip, limit):
    table = db.get_db().yanfuNewsDB.newsTable
    skip = int(skip)
    limit = int(limit)
    condition = {}
    data = table.find(condition, field).sort('time', pymongo.DESCENDING).skip(skip)
    if not limit:
        data.limit(limit)
    return list(data)


# 查找标题中包含word_list任意词语的新闻
def query_search(time_start, time_end, order, search_words, skip, limit):
    skip = int(skip)
    limit = int(limit)
    table_news = db.get_db().yanfuNewsDB.newsTable
    table_index = db.get_db().yanfuNewsDB.tagIndexTable

    articles = set()

    tag_name_limit = {'$in': search_words}
    index_rows = table_index.find({'tag_name': tag_name_limit})
    for a_index_row in index_rows:
        articles = set.union(articles, set(a_index_row['articles']))
    time_limit = {
        '$gte': time_start,
        '$lte': time_end,
    }
    id_limit = {'$in': list(articles)}
    if search_words:
        condition = {
            '_id': id_limit,
            'time': time_limit
        }
        data = table_news.find(condition, field)
    # 都不选等于全选
    else:
        condition = {'time': time_limit}
        data = table_news.find(condition, field)
    if order == 'by_time':
        data = data.sort('time', pymongo.DESCENDING)
    else:
        data = data.sort('time', pymongo.ASCENDING)
    count = data.count()
    data = data.skip(skip)
    if limit:
        data = data.limit(limit)
    return [list(data), count]


def delete(news_id):
    news_id = int(news_id)
    table = db.get_db().yanfuNewsDB.newsTable
    condition = {'_id': news_id}
    table.delete_one(condition)
