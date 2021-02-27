import json

from flask import request, Blueprint

from db import db_news, db_index
from global_var import TAG_ID_MAP, SESSION_MAP, ID_TAG_MAP

bp_tag = Blueprint('tag', __name__, url_prefix='/service')


# 删除标签，需要news_id,tag_name,session_id
@bp_tag.route('/delete_tag', methods=['GET', 'POST'])
def delete_tag_service():
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
            if 'tag_name' in request.values:
                tag_name = request.values.get('tag_name')
                # 搜到news
                news = db_news.query_one(news_id)
                # 在常量表中则用id，不在则直接用内容
                print(news['tags'])
                if tag_name in TAG_ID_MAP:
                    # 所删除的tag已被转换为常量
                    if TAG_ID_MAP[tag_name] in news['static_tags']:
                        news['static_tags'].remove(TAG_ID_MAP[tag_name])
                        db_index.delete_one(TAG_ID_MAP[tag_name], news_id)
                    # 还未转化，到tags中删
                    else:
                        news['tags'].remove(tag_name)
                else:
                    news['tags'].remove(tag_name)

                # 重新写入
                db_news.update_one_tags(news_id, news['static_tags'], news['tags'])
                rtn = 1
                message = '删除成功'
            else:
                message = '请输入tag_name'
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


# 添加标签
@bp_tag.route('/add_tag', methods=['GET', 'POST'])
def add_tag_service():
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
            if 'tag_name' in request.values:
                tag_name = request.values.get('tag_name')
                news = db_news.query_one(news_id)
                # tag在常量表中，放入static_tags
                if tag_name in TAG_ID_MAP:
                    news['static_tags'].append(TAG_ID_MAP[tag_name])
                    db_index.add_one(TAG_ID_MAP[tag_name], news_id)
                else:
                    news['tags'].append(tag_name)
                # 重新写入
                rtn = 1
                db_news.update_one_tags(news_id, news['static_tags'], news['tags'])
                message = '添加成功'
            else:
                message = '请输入tag_name'
        else:
            message = '请输入news_id'
    else:
        return '权限不足，只有管理员可以修改'
    data = {
        'rtn': rtn,
        'message': message
    }
    data = json.dumps(data, ensure_ascii=False)
    return data


@bp_tag.route('/change_info', methods=['GET', 'POST'])
def change_info_service():
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
            news = db_news.query_one(news_id)
            if news:
                if 'author' in request.values and 'category' in request.values and 'stock' in request.values:
                    author = request.values.get('author')
                    category = request.values.get('category')
                    stock = request.values.get('stock')
                    if news['author'] in ID_TAG_MAP:
                        db_index.delete_one(news['author'], news_id)
                    if news['category'] in ID_TAG_MAP:
                        db_index.delete_one(news['category'], news_id)
                    if news['stock'] in ID_TAG_MAP:
                        db_index.delete_one(news['stock'], news_id)
                    # 替换为id添加,如果存在于常量表则替换为id添加，且修改倒排索引表
                    if author in TAG_ID_MAP:
                        author = TAG_ID_MAP[author]
                        db_index.add_one(author, news_id)
                    if category in TAG_ID_MAP:
                        category = TAG_ID_MAP[category]
                        db_index.add_one(category, news_id)
                    if stock in TAG_ID_MAP:
                        stock = TAG_ID_MAP[stock]
                        db_index.add_one(stock, news_id)
                    news['author'] = author
                    news['category'] = category
                    news['stock'] = stock
                    # 重新写入
                    db_news.update_one_info(news_id, author, category, stock)
                    rtn = 1
                    message = '修改成功'

                else:
                    message = '请输入完整参数'
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
