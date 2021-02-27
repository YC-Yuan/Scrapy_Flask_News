import json
from flask import request, Blueprint
from db import db_news
from global_var import SESSION_MAP

bp_delete = Blueprint('delete', __name__, url_prefix='/service')


# 获取具体新闻
@bp_delete.route('/delete', methods=['GET', 'POST'])
def delete():
    rtn = 0
    # 查看登陆状态,检验权限
    permission = 0
    if 'session_id' in request.values:
        tmp = int(request.values.get('session_id'))
        if tmp in SESSION_MAP:
            session_id = tmp
            permission = SESSION_MAP[session_id][1]

    # 有修改权限
    if permission > 1:
        # 读取参数
        if 'news_id' in request.values:
            news_id = int(request.values.get('news_id'))
            # 搜到news
            news = db_news.query_one(news_id)
            if news:
                # 删除
                db_news.delete(news_id)
                rtn = 1
                message = '删除成功'
            else:
                message = 'news_id不存在，请检查是否正确'
        else:
            message = '请输入news_id'
    else:
        message = '权限不足，只有管理员可以修改'
    data = {
        'rtn': rtn,
        'message': message
    }
    data = json.dumps(data, ensure_ascii=False)
    return data
