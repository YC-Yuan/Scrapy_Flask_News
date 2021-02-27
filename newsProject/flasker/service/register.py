import json
from flask import request, Blueprint
from db import db_users

bp_register = Blueprint('register', __name__, url_prefix='/service')


# 注册
@bp_register.route('/register', methods=['POST'])
def register():
    rtn = 0

    email = request.values.get('email') or None
    password = request.values.get('password') or None

    if not (email and password):
        message = '请确保已输入邮箱和密码'

    elif db_users.exist(email):
        message = '邮箱已被注册，请更换'
    # 邮箱密码都输入，且邮箱未重复，允许注册
    else:
        rtn = 1
        db_users.insert(email, password)
        message = '注册成功，可以登录了'

    data = {
        'rtn': rtn,
        'message': message
    }
    data = json.dumps(data, ensure_ascii=False)
    return data
