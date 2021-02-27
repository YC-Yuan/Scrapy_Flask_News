import csv
import json
import os
from threading import Timer

from datetime import datetime
from pypinyin import pinyin, Style
from itertools import chain
from utils import snowflake


def to_pinyin(s):
    return ''.join(chain.from_iterable(pinyin(s, style=Style.TONE3)))


# session存储，其中放置session_id-[user_id,permission]
SESSION_MAP = dict()

# 放置session_id-新闻<id-标题>、历史id Set
SESSION_NEWS_MAP = dict()
SESSION_HISTORY_MAP = dict()

# 设置session保存时间，单位为秒
SESSION_INTERVAL = 1200

# 推荐每页展示数
RECOMMEND_SIZE = 12
SEARCH_SIZE = 12
BROWSE_SIZE = 12

# 字段id_name常量表
current_abs_path = os.getcwd()
tag_id_path = os.path.join(current_abs_path, 'static', 'tag_id', 'tag_id.csv')
tag_category = os.path.join(current_abs_path, 'static', 'tag_id', 'tag_category.csv')

TAG_ID_MAP = dict()
ID_TAG_MAP = dict()
TAG_CATEGORY_PREFIX_MAP = dict()
TAG_CATEGORY_ID_MAP = dict()
TAG_LISTS_MAP = dict()

# 载入一级常量表，以dict形式存储类别-类别编号
with open(tag_category, 'r', encoding='GBK') as f:
    reader = csv.reader(f)
    for row in reader:
        row_id = int(row[0])
        TAG_CATEGORY_PREFIX_MAP[row[1]] = row_id
        TAG_CATEGORY_ID_MAP[row_id] = row[1]
        TAG_LISTS_MAP[row_id] = list()

# 载入二级常量表，以dict形式存储tag-tag编号
with open(tag_id_path, 'r', encoding='GBK') as f:
    reader = csv.reader(f)
    # [0]为id，[1]为内容
    for row in reader:
        row_id = int(row[0])
        ID_TAG_MAP[row_id] = row[1]
        TAG_ID_MAP[row[1]] = row_id
        # 载入分块常量表，根据一级表分类，记录各个类别的tag有哪些
        TAG_LISTS_MAP[int(row_id / 100000)].append(row[1])
for list_index in TAG_LISTS_MAP:
    TAG_LISTS_MAP[list_index].sort(key=pinyin)

# 配置的ip和端口
URL_PREFIX = 'http://127.0.0.1:5000'

SNOW_NEWS = snowflake.MySnow("00")
SNOW_USER = snowflake.MySnow("01")
SNOW_SESSION = snowflake.MySnow("02")
SNOW_HISTORY = snowflake.MySnow("03")


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)
