import json
from flask import request, Blueprint

from db import db_news
from global_var import SESSION_MAP, SESSION_NEWS_MAP, DateEncoder, RECOMMEND_SIZE

bp_recommend = Blueprint('recommend', __name__, url_prefix='/service')


# 获取推荐
@bp_recommend.route('/recommend', methods=['GET', 'POST'])
def recommend():
    rtn = 0
    page = 1
    size = RECOMMEND_SIZE
    # 查看登陆状态
    session_id = 0
    if 'session_id' in request.values:
        if int(request.values.get('session_id')) in SESSION_MAP:
            session_id = int(request.values.get('session_id'))

    # 读取参数
    if 'page' in request.values:
        page = int(request.values.get('page'))

    post_data = list()
    news_size = 0
    # 登录状态下,从内存中查找未读信息
    if session_id:
        news_list = SESSION_NEWS_MAP[session_id]
        news_size = len(news_list)
        start = size * page - size
        end = min(page * size, news_size)
        post_data = news_list[start:end]
        if len(post_data) > 0:
            rtn = 1
            message = '查询成功'
        else:
            message = '查询失败'
    # 访客状态下，广泛查找信息
    else:
        rtn = 0
        message = 'session_id错误或过期，请重新登录'

    result = {
        'rtn': rtn,
        'message': message,
        'post_data': post_data,
        'news_size': news_size,
    }

    result = json.dumps(result, ensure_ascii=False, cls=DateEncoder)
    return result
