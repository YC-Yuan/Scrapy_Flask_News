import json
from flask import request, Blueprint

from db import db_news
from global_var import SESSION_MAP, DateEncoder, SESSION_HISTORY_MAP

bp_show = Blueprint('show', __name__, url_prefix='/service')


# 获取具体新闻
@bp_show.route('/show', methods=['GET', 'POST'])
def show():
    rtn = 0
    # 查看登陆状态
    session_id = 0
    if 'session_id' in request.values:
        tmp = int(request.values.get('session_id'))
        if tmp in SESSION_MAP:
            session_id = tmp

    if not session_id:
        result = {
            'rtn': 0,
            'post_data': list(),
            'news_size': 0,
            'message': 'session_id错误或过期，请重新登录',
        }
        result = json.dumps(result, ensure_ascii=False, cls=DateEncoder)
        return result

    if 'news_id' in request.values:
        news_id = request.values.get('news_id')
        post_data = db_news.query_one(news_id)
        if not post_data:
            message = '不存在此条新闻，请检查news_id'
        else:
            # 登录状态下,还需要修改history
            if session_id:
                SESSION_HISTORY_MAP[session_id].add(news_id)
            data = {
                'rtn': 1,
                'message': '获取新闻成功',
                'post_data': post_data
            }
            result = json.dumps(data, ensure_ascii=False, cls=DateEncoder)
            return result
    else:
        message = '请输入news_id'
    data = {
        'rtn': rtn,
        'message': message
    }
    data = json.dumps(data, ensure_ascii=False)
    return data
