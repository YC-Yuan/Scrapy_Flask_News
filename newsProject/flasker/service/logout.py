import json

from flask import request, Blueprint
from global_var import SESSION_MAP
from service import login

bp_logout = Blueprint('logout', __name__, url_prefix='/service')


# 登出
@bp_logout.route('/logout', methods=['POST'])
def logout():
    rtn = 0
    # 查看登陆状态
    if 'session_id' in request.values:
        session_id = int(request.values.get('session_id'))
        # 检验提交的session
        if session_id in SESSION_MAP:
            login.update_history(session_id)
            rtn = 1
            message = '已成功登出'
        else:
            message = 'session_id错误，登出无效'
    else:
        message = '请确保已输入session_id'
    data = {
        'rtn': rtn,
        'message': message
    }
    data = json.dumps(data, ensure_ascii=False)
    return data
