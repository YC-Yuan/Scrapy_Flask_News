import db.db_base as db


def query_one(index_id):
    index_id = int(index_id)
    table = db.get_db().yanfuNewsDB.tagIndexTable
    condition = {'_id': index_id}
    return table.find_one(condition)


def insert_one(index_id, tag_name, articles):
    index_id = int(index_id)
    table = db.get_db().yanfuNewsDB.tagIndexTable
    insert = {
        '_id': index_id,
        'tag_name': tag_name,
        'articles': articles,
    }
    table.insert_one(insert)


def update_one(index_id, articles):
    index_id = int(index_id)
    table = db.get_db().yanfuNewsDB.tagIndexTable
    condition = {'_id': index_id}
    update = {'$set': {
        'articles': articles
    }}
    table.update_one(condition, update)


def add_one(index_id, news_id):
    index_id = int(index_id)
    news_id = int(news_id)
    table = db.get_db().yanfuNewsDB.tagIndexTable

    condition = {'_id': index_id}
    index_row = table.find_one(condition)
    if index_row:
        if news_id not in index_row['articles']:
            index_row['articles'].append(news_id)
            update_one(index_id, index_row['articles'])


def delete_one(index_id, news_id):
    index_id = int(index_id)
    news_id = int(news_id)
    table = db.get_db().yanfuNewsDB.tagIndexTable

    condition = {'_id': index_id}
    index_row = table.find_one(condition)
    if index_row:
        if news_id in index_row['articles']:
            index_row['articles'].remove(news_id)
            update_one(index_id, index_row['articles'])
