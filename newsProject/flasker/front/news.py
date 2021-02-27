import json
import math
from urllib import request

from flask import Blueprint, render_template, session, request, redirect, url_for
import urllib.parse
from global_var import RECOMMEND_SIZE, URL_PREFIX, ID_TAG_MAP, TAG_ID_MAP, SESSION_MAP, SEARCH_SIZE, \
    TAG_LISTS_MAP, TAG_CATEGORY_ID_MAP

bp_news = Blueprint('news', __name__, url_prefix='/news')


@bp_news.route('/recommend', methods=['GET', 'POST'])
def recommend():
    return recommend_page(1)


@bp_news.route('/recommend/<page>', methods=['GET', 'POST'])
def recommend_page(page):
    page = int(page)
    form = {
        'page': page
    }

    # 未登录则要求登录
    if 'session_id' not in session and 'session_id' not in request.form:
        return render_template('/users/login.html', message='未登录或在线超时，请登录')
    if 'session_id' in session:
        form['session_id'] = session['session_id']
    if 'session_id' in request.form:
        form['session_id'] = request.form['session_id']
    if int(form['session_id']) not in SESSION_MAP:
        return render_template('/users/login.html', message='未登录或在线超时，请登录')

    post_data = bytes(urllib.parse.urlencode(form), encoding='utf-8')
    response = urllib.request.urlopen(URL_PREFIX + '/service/recommend', data=post_data)
    data = response.read().decode()
    # data属性查看文档接口
    data = json.loads(data)
    # 替换tag，以文字而非id展示
    for a_news in data['post_data']:
        static_tags = list()
        for a_tag in a_news['static_tags']:
            static_tags.append(ID_TAG_MAP[a_tag])
        a_news['static_tags'] = static_tags
        if a_news['author'] in ID_TAG_MAP:
            a_news['author'] = ID_TAG_MAP[a_news['author']]
        if a_news['category'] in ID_TAG_MAP:
            a_news['category'] = ID_TAG_MAP[a_news['category']]
        if a_news['stock'] in ID_TAG_MAP:
            a_news['stock'] = ID_TAG_MAP[a_news['stock']]
        a_news['tags'] = a_news['static_tags'] + a_news['tags']
    page_num = max(1, math.ceil(data['news_size'] / RECOMMEND_SIZE))
    return render_template('/news/recommend.html', data=data['post_data'], page_num=page_num, page=page, form=form,
                           tag_id_map=TAG_ID_MAP)


@bp_news.route('/search', methods=['GET', 'POST'])
def search():
    return search_page(1)


@bp_news.route('/search/<page>', methods=['GET', 'POST'])
def search_page(page):
    page = int(page)
    if 'page' in request.values:
        page = int(request.values['page'])

    form = {
        'page': page,
    }
    # 未登录则要求登录
    if 'session_id' not in session and 'session_id' not in request.form:
        return render_template('/users/login.html', message='未登录或在线超时，请登录')
    if 'session_id' in session:
        form['session_id'] = session['session_id']
    if 'session_id' in request.form:
        form['session_id'] = request.form['session_id']
    if int(form['session_id']) not in SESSION_MAP:
        return render_template('/users/login.html', message='未登录或在线超时，请登录')

    if 'time_range' in request.values:
        form['time_range'] = request.values.get('time_range')
    if 'order' in request.values:
        form['order'] = request.values.get('order')
    if 'search_words' in request.values:
        form['search_words'] = '.'.join(request.values.getlist('search_words'))
    post_data = bytes(urllib.parse.urlencode(form), encoding='utf-8')
    response = urllib.request.urlopen(URL_PREFIX + '/service/search', data=post_data)
    data = response.read().decode()
    # data属性查看文档接口
    data = json.loads(data)
    if 'search_words' in form:
        search_words = form['search_words']
        form['search_words'] = set(search_words.split('.'))
        # 替换id和内容
    for a_news in data['post_data']:
        static_tags = list()
        for a_tag in a_news['static_tags']:
            static_tags.append(ID_TAG_MAP[a_tag])
        a_news['static_tags'] = static_tags
        if a_news['author'] in ID_TAG_MAP:
            a_news['author'] = ID_TAG_MAP[a_news['author']]
        if a_news['category'] in ID_TAG_MAP:
            a_news['category'] = ID_TAG_MAP[a_news['category']]
        if a_news['stock'] in ID_TAG_MAP:
            a_news['stock'] = ID_TAG_MAP[a_news['stock']]
        a_news['tags'] = a_news['static_tags'] + a_news['tags']
    page_num = max(1, math.ceil(data['news_size'] / SEARCH_SIZE))
    return render_template('/news/search.html', data=data['post_data'], page_num=page_num, page=page, form=form,
                           tag_id_map=TAG_ID_MAP, id_tag_category_map=TAG_CATEGORY_ID_MAP, tag_lists=TAG_LISTS_MAP)


@bp_news.route('/show/<news_id>')
def show(news_id):
    news_id = int(news_id)
    form = {
        'news_id': news_id
    }

    # 未登录则要求登录
    if 'session_id' not in session and 'session_id' not in request.form:
        return render_template('/users/login.html', message='未登录或在线超时，请登录')
    if 'session_id' in session:
        form['session_id'] = session['session_id']
    if 'session_id' in request.form:
        form['session_id'] = request.form['session_id']
    if int(form['session_id']) not in SESSION_MAP:
        return render_template('/users/login.html', message='未登录或在线超时，请登录')
    else:
        session_id = int(form['session_id'])
        permission = SESSION_MAP[session_id][1]

    post_data = bytes(urllib.parse.urlencode(form), encoding='utf-8')
    response = urllib.request.urlopen(URL_PREFIX + '/service/show', data=post_data)
    data = response.read().decode()
    data = json.loads(data)
    if data['rtn']:
        a_news = data['post_data']
        # 替换tag
        static_tags = list()
        for a_tag in a_news['static_tags']:
            static_tags.append(ID_TAG_MAP[a_tag])
        a_news['static_tags'] = static_tags
        if a_news['author'] in ID_TAG_MAP:
            a_news['author'] = ID_TAG_MAP[a_news['author']]
        if a_news['category'] in ID_TAG_MAP:
            a_news['category'] = ID_TAG_MAP[a_news['category']]
        if a_news['stock'] in ID_TAG_MAP:
            a_news['stock'] = ID_TAG_MAP[a_news['stock']]
        a_news['tags'] = a_news['static_tags'] + a_news['tags']
        tags = TAG_ID_MAP.keys()
        # 22、21分别为发布者和类别常量的前缀
        return render_template('/news/show.html', data=a_news, form=form, tags=tags, permission=permission, tag_id_map=TAG_ID_MAP,
                               authors=TAG_LISTS_MAP[22], categories=TAG_LISTS_MAP[21], stocks=TAG_LISTS_MAP[90])
    else:
        return data['message']


@bp_news.route('/delete/<news_id>')
def delete(news_id):
    news_id = int(news_id)
    form = {
        'news_id': news_id,
        'session_id': session['session_id']
    }
    post_data = bytes(urllib.parse.urlencode(form), encoding='utf-8')
    response = urllib.request.urlopen(URL_PREFIX + '/service/delete', data=post_data)
    data = response.read().decode()
    data = json.loads(data)
    if data['rtn']:
        return redirect(URL_PREFIX + '/news/recommend')
    else:
        return data['message']


@bp_news.route('/delete_tag/<news_id>/<tag_name>')
def delete_tag(news_id, tag_name):
    news_id = int(news_id)
    form = {
        'news_id': news_id,
        'tag_name': tag_name,
        'session_id': session['session_id']
    }
    post_data = bytes(urllib.parse.urlencode(form), encoding='utf-8')
    response = urllib.request.urlopen(URL_PREFIX + '/service/delete_tag', data=post_data)
    data = response.read().decode()
    data = json.loads(data)
    if data['rtn']:
        return redirect(URL_PREFIX + '/news/show/' + str(news_id))
    else:
        return data['message']


@bp_news.route('/add_tag/<news_id>')
def add_tag(news_id):
    news_id = int(news_id)
    tag_name = request.values.get('tag_name')
    form = {
        'news_id': news_id,
        'tag_name': tag_name,
        'session_id': session['session_id']
    }
    post_data = bytes(urllib.parse.urlencode(form), encoding='utf-8')
    response = urllib.request.urlopen(URL_PREFIX + '/service/add_tag', data=post_data)
    data = response.read().decode()
    data = json.loads(data)
    if data['rtn']:
        return redirect(URL_PREFIX + '/news/show/' + str(news_id))
    else:
        return data['message']


@bp_news.route('/change_info/<news_id>')
def change_info(news_id):
    news_id = int(news_id)
    author = request.values.get('author')
    category = request.values.get('category')
    stock = request.values.get('stock')
    form = {
        'news_id': news_id,
        'category': category,
        'author': author,
        'stock': stock,
        'session_id': session['session_id']
    }
    post_data = bytes(urllib.parse.urlencode(form), encoding='utf-8')
    response = urllib.request.urlopen(URL_PREFIX + '/service/change_info', data=post_data)
    data = response.read().decode()
    data = json.loads(data)
    if data['rtn']:
        return redirect(URL_PREFIX + '/news/show/' + str(news_id))
    else:
        return data['message']
