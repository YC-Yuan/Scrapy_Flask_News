import db.db_base as db
import datetime
from global_var import SNOW_HISTORY


# 新建浏览历史
def insert_history(user_id, news_id):
    table = db.get_db().yanfuNewsDB.historyTable
    user_id = int(user_id)
    news_id = int(news_id)
    condition = {
        'user_id': user_id,
        'news_id': news_id,
    }
    find = table.find_one(condition)
    if not find:  # 避免重复插入
        _id = int(SNOW_HISTORY.get_id())
        user_id = int(user_id)
        news_id = int(news_id)
        time_now = datetime.datetime.now()
        history = {
            '_id': _id,
            'user_id': user_id,
            'news_id': news_id,
            'time': time_now
        }
        table.insert(history)


# 根据user_id查询所有新闻id，用于修剪
def query_all(user_id):
    user_id = int(user_id)
    table = db.get_db().yanfuNewsDB.historyTable
    condition = {'user_id': user_id}
    field = {'user_id': 1, 'news_id': 1}
    data = table.find(condition, field)
    return list(data)


# 根据user_id查询history
def query_user_history(user_id):
    user_id = int(user_id)
    table = db.get_db().yanfuNewsDB.historyTable
    condition = {'user_id': user_id}
    history = table.find(condition)
    return list(history)


# 根据news_id查询history
def query_news_history(news_id):
    news_id = int(news_id)
    table = db.get_db().yanfuNewsDB.historyTable
    condition = {'news_id': news_id}
    history = table.find(condition)
    return list(history)
