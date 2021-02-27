import json
import urllib.parse
import urllib.request
from global_var import TAG_ID_MAP, URL_PREFIX
from flask import Blueprint, render_template, request, redirect, url_for, session

bp_users = Blueprint('users', __name__, url_prefix='/users')


@bp_users.route('/register')
def register():
    return render_template('/users/register.html')


# register.html提交到这里
@bp_users.route('/register_handle', methods=["POST"])
def register_handle():
    email = request.values.get('email')
    password = request.values.get('password')
    form = {
        'email': email,
        'password': password,
    }
    form = bytes(urllib.parse.urlencode(form), encoding='utf-8')
    response = urllib.request.urlopen(URL_PREFIX+'/service/register', data=form)
    data = response.read().decode()
    # 成功则跳转到登录界面
    data = json.loads(data)
    if data.get('rtn'):
        return render_template('/users/login.html', message=data.get('message'))
    else:
        return render_template('/users/register.html', message=data.get('message'))


@bp_users.route('/login')
def login():
    return render_template('/users/login.html', tag_id_map=TAG_ID_MAP)


# login.html提交到这里
@bp_users.route('/login_handle', methods=["POST"])
def login_handle():
    email = request.values.get('email')
    password = request.values.get('password')
    # 向接口发送http请求
    form = {
        'email': email,
        'password': password,
    }
    form = bytes(urllib.parse.urlencode(form), encoding='utf-8')
    response = urllib.request.urlopen(URL_PREFIX+'/service/login', data=form)
    data = response.read().decode()
    # 登陆成功，在浏览器中保存session_id
    data = json.loads(data)
    if 'session_id' in data:
        session['session_id'] = data.get('session_id')
        return redirect(url_for('news.recommend'))
    # 登陆失败
    else:
        return render_template('/users/login.html', message=data.get('message'))


@bp_users.route('/logout')
def logout():
    form = {}
    # 获取参数
    if 'session_id' in session:
        form['session_id'] = session['session_id']
        # 清除浏览器中的session
        session.pop('session_id', None)
    # 登出，将自定义session也发送过去清除
    form = bytes(urllib.parse.urlencode(form), encoding='utf-8')
    urllib.request.urlopen(URL_PREFIX+'/service/logout', data=form)
    # 登出后重定向到recommend
    return redirect(url_for('users.login'))
