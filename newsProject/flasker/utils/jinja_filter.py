from datetime import datetime

from flask import Blueprint

bp_filter = Blueprint('filter', __name__)


@bp_filter.app_template_filter('page_range')
def page_range(page, page_num):
    page_size = 5
    page_delta = int(page_size / 2)

    page = int(page)
    page_num = int(page_num)
    if page_num <= page_size:
        return [1, page_num]
    else:
        end = min(page + page_delta, page_num)
        start = max(1, end - page_size + 1)
        end = min(start + page_size - 1, page_num)
    return [start, end]


@bp_filter.app_template_filter('time_display')
def time_display(time):
    # xxxx-xx-xx xx:xx:xx
    # 0123456789012345678
    time = datetime(int(time[0:4]), int(time[5:7]), int(time[8:10]), int(time[11:13]), int(time[14:16]), int(time[17:]))
    delta = datetime.now() - time

    year_days = 365
    month_days = 30
    week_days = 7
    hour_seconds = 3600
    minute_seconds = 60

    num = delta.days
    tmp = num // year_days
    if tmp > 0:
        return str(tmp) + '年前'
    tmp = num // month_days
    if tmp > 0:
        return str(tmp) + '个月前'
    tmp = num // week_days
    if tmp > 0:
        return str(tmp) + '周前'
    if num > 0:
        return str(num) + '天前'
    num = delta.seconds
    tmp = num // hour_seconds
    if tmp > 0:
        return str(tmp) + '小时前'
    tmp = num // minute_seconds
    if tmp > 0:
        return str(tmp) + '分钟前'
    num = num % minute_seconds
    return str(num) + '秒前'
