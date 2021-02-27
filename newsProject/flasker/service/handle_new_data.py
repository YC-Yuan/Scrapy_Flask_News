import json
from flask import request, Blueprint

from db import db_base, db_news, db_index
from global_var import DateEncoder, SESSION_HISTORY_MAP, TAG_ID_MAP

# 爬虫将调用此接口，通知服务器处理新爬取入库的新闻
# 新增新闻将进行关键词过滤，修改倒排索引表

bp_handle_new_data = Blueprint('handle_new_data', __name__, url_prefix='/service')

# 新爬取的新闻记录在newsCacheTable中，逐条取出并根据常量表转化、构建索引
@bp_handle_new_data.route('/handle_new_data', methods=['POST'])
def handle():
    message = ''
    rtn = 0
    if 'key' in request.values:
        key = request.values.get('key')
        # 检测口令
        if key == 'YanFuNews_NewsTable':
            if 'news_id' in request.values:
                news_id = request.values.get('news_id')
                if news_id.isdigit():
                    news_id = int(news_id)
                    a_news = db_news.query_one(news_id)
                    if a_news:
                        index_list = list()
                        tag_list = a_news['tags']
                        static_tag_list = a_news['static_tags']
                        author = a_news['author']
                        category = a_news['category']

                        for a_tag in a_news['tags']:
                            if a_tag in TAG_ID_MAP:
                                tag_list.remove(a_tag)
                                static_tag_list.append(TAG_ID_MAP[a_tag])
                        if author in TAG_ID_MAP:
                            author = TAG_ID_MAP[author]
                            index_list.append(TAG_ID_MAP[author])
                        if category in TAG_ID_MAP:
                            category = TAG_ID_MAP[category]
                            index_list.append(TAG_ID_MAP[category])
                        db_news.update_one_tags(news_id, static_tag_list, tag_list)
                        db_news.update_one_info(news_id, author, category)
                        # 至此完成了新闻本身的信息更新

                        # 接下来更改倒排索引
                        index_list += static_tag_list
                        for index in index_list:
                            # 先搜旧有的，拼接后插入
                            old_row = db_index.query_one(index)
                            news_list = old_row['articles']
                            news_list.append(news_id)
                            db_index.update_one(index, news_list)
                        rtn = 1
                        message = '处理完成'
                    else:
                        message = '数据库中不存在此新闻'
                else:
                    message = 'news_id格式错误'
        else:
            message = 'key口令错误'
    else:
        message = '缺少key'

    if not rtn:
        message += '，此接口仅供爬虫模组调用，请查看文档'

    result = {
        'rtn': rtn,
        'message': message,
    }

    result = json.dumps(result, ensure_ascii=False, cls=DateEncoder)
    return result
