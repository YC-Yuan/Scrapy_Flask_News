import json

from threading import Timer
from flask import request, Blueprint, session
from db import db_users, db_history, db_conbine
from global_var import SNOW_SESSION, SESSION_MAP, SESSION_NEWS_MAP, SESSION_HISTORY_MAP, SESSION_INTERVAL

bp_login = Blueprint('login', __name__, url_prefix='/service')


def update_history(session_id):
    # 先判断session还是否存在
    if session_id in SESSION_MAP:
        user_id = SESSION_MAP[session_id][0]
        history = SESSION_HISTORY_MAP[session_id]

        # a_history即为news_id
        for a_history in history:
            db_history.insert_history(user_id, a_history)

        del SESSION_MAP[session_id]
        del SESSION_NEWS_MAP[session_id]
        del SESSION_HISTORY_MAP[session_id]


# 登录
@bp_login.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.values.get('email') or None
        password = request.values.get('password') or None
        if not (email and password):
            message = "请确保已输入邮箱和密码"
        else:
            # 检验登录情况
            user_id = db_users.login_check(email, password)
            # 登陆成功！
            if user_id:
                # 设置session
                permission = db_users.permission_check(user_id)
                session_id = SNOW_SESSION.get_id()
                SESSION_MAP[session_id] = [user_id, permission]  # 在session池中保存登陆的用户

                # 浏览器session不在这里保存，这里是urllib包发出的请求
                data = {
                    'rtn': 1,
                    'session_id': session_id,
                    'message': "登陆成功"
                }
                data = json.dumps(data, ensure_ascii=False)

                # 以list结构加载新闻id和标题到内存中,与session_id对应
                SESSION_NEWS_MAP[session_id] = db_conbine.query_new_news(user_id)
                SESSION_HISTORY_MAP[session_id] = set()

                timer = Timer(SESSION_INTERVAL, update_history, [session_id])
                timer.start()

                # 返回session值供使用
                return data
            # 登陆失败
            else:
                message = '登录失败，用户名或密码错误'
    else:
        message = '请使用POST请求'
    data = {
        'rtn': 0,
        'message': message
    }
    data = json.dumps(data, ensure_ascii=False)
    return data
