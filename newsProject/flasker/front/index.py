from flask import Blueprint, redirect, url_for, render_template

bp_index = Blueprint('index', __name__)


@bp_index.route('/', methods=['GET', 'POST'])
def index():
    return render_template('/users/login.html', message='未登录或在线超时，请登录')
