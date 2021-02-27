import json
from datetime import datetime

from flask import request, Blueprint

from db import db_news
from global_var import DateEncoder, SEARCH_SIZE, SESSION_MAP

bp_search = Blueprint('search', __name__, url_prefix='/service')


@bp_search.route('/search', methods=['GET', 'POST'])
def search():
    page = 1
    size = SEARCH_SIZE
    time_range = '2021-01-01 - ' + datetime.now().strftime('%Y-%m-%d')
    order = 'by_time'
    search_words = []

    # 查看登陆状态
    session_id = 0
    if 'session_id' in request.values:
        if int(request.values.get('session_id')) in SESSION_MAP:
            session_id = int(request.values.get('session_id'))

    if not session_id:
        result = {
            'rtn': 0,
            'post_data': list(),
            'news_size': 0,
            'message': 'session_id错误或过期，请重新登录',
        }
        result = json.dumps(result, ensure_ascii=False, cls=DateEncoder)
        return result

    # 读取参数
    if 'page' in request.values:
        page = int(request.values.get('page'))

    if 'time_range' in request.values:
        time_range = request.values.get('time_range')
    if 'order' in request.values:
        order = request.values.get('order')
    if 'search_words' in request.values:
        search_words = request.values.get('search_words').split('.')

    # 将参数转化为需要的形式
    year = int(time_range[0:4])
    month = int(time_range[5:7])
    day = int(time_range[8:10])
    time_start = datetime(year, month, day, 0, 0, 0, 0)
    year = int(time_range[13:17])
    month = int(time_range[18:20])
    day = int(time_range[21:])
    time_end = datetime(year, month, day, 23, 59, 59, 9999)

    start = size * page - size
    # [数据,数量]形式返回
    search_result = db_news.query_search(time_start, time_end, order, search_words, start, SEARCH_SIZE)
    post_data = search_result[0]
    news_size = search_result[1]
    result = {
        'rtn': 1,
        'post_data': post_data,
        'news_size': news_size,
        'message': '查询成功',
    }

    result = json.dumps(result, ensure_ascii=False, cls=DateEncoder)
    return result
