import csv
import os

import pymongo

field = {
    '_id': 1,
    'author': 1,
    'category': 1,
    'stock': 1,
    'tags': 1,
    'static_tags': 1,
}  # 过滤不需要的字段，减少内存占用


class LoadUtils:
    # 遍历整个数据库，将tag尽可能转化为tag常量表中的id
    @staticmethod
    def load_all_tag():
        maps = LoadUtils.get_static_map()
        tag_id_map = maps[0]

        db = pymongo.MongoClient('127.0.0.1', 27017)
        table = db.yanfuNewsDB.newsTable
        news_list = list(table.find({}, field))
        for a_news in news_list:
            tags_list = a_news['tags']
            static_tags_list = a_news['static_tags']
            # 将分词结果过滤进常量tag表
            for a_tag in tags_list:
                # 数字tag添加到常量标签中
                if isinstance(a_tag, int):
                    static_tags_list.append(a_tag)
                    tags_list.remove(a_tag)
                else:
                    if a_tag in tag_id_map:
                        static_tags_list.append(tag_id_map[a_tag])
                        tags_list.remove(a_tag)
            # 将作者、类别字段过滤为tag常量
            if a_news['author'] in tag_id_map:
                a_news['author'] = tag_id_map[a_news['author']]
            if a_news['category'] in tag_id_map:
                a_news['category'] = tag_id_map[a_news['category']]
            if a_news['stock'] in tag_id_map:
                a_news['stock'] = tag_id_map[a_news['stock']]
            # 更新数据库
            condition = {'_id': a_news['_id']}
            update = {'$set': {
                'static_tags': static_tags_list,
                'tags': tags_list,
                'author': a_news['author'],
                'category': a_news['category'],
                'stock': a_news['stock'],
            }}
            table.update_one(condition, update)
        db.close()

    # 遍历整个数据库，将id形式的tag全部转化为string
    @staticmethod
    def unload_all_tag():
        maps = LoadUtils.get_static_map()
        id_tag_map = maps[1]

        db = pymongo.MongoClient('127.0.0.1', 27017)
        table = db.yanfuNewsDB.newsTable
        # 获取所有新闻并遍历
        news_list = list(table.find({}, field))
        for a_news in news_list:
            static_tags_list = a_news['static_tags']
            unload_tags_list = a_news['tags']
            # 逐个将数字转回
            for a_tag in static_tags_list:
                unload_tags_list.append(id_tag_map[a_tag])
                static_tags_list.remove(a_tag)

            # 将作者、类别字段过滤为tag常量
            if a_news['author'] in id_tag_map:
                a_news['author'] = id_tag_map[a_news['author']]
            if a_news['category'] in id_tag_map:
                a_news['category'] = id_tag_map[a_news['category']]
            if a_news['stock'] in id_tag_map:
                a_news['stock'] = id_tag_map[a_news['stock']]
            # 更新数据库
            condition = {'_id': a_news['_id']}
            update = {'$set': {
                'static_tags': static_tags_list,
                'tags': unload_tags_list,
                'author': a_news['author'],
                'category': a_news['category'],
                'stock': a_news['stock'],
            }}
            table.update_one(condition, update)
        db.close()

    @staticmethod
    # 遍历整个数据库，记录含有常量表中tag的文章，构建倒排索引
    def construct_revers_index():
        db = pymongo.MongoClient('127.0.0.1', 27017)
        table_news = db.yanfuNewsDB.newsTable
        table_index = db.yanfuNewsDB.tagIndexTable
        table_index.drop()

        maps = LoadUtils.get_static_map()
        id_tag_map = maps[1]

        # 先插入所有tag
        for _id in id_tag_map:
            insert = {
                '_id': _id,
                'tag_name': id_tag_map[_id],
                'articles': list(),
            }
            table_index.insert_one(insert)

        # 遍历新闻，收集每个tag对应的文章
        news_list = table_news.find({}, field)
        index_news_set = dict()

        for a_news in news_list:
            index_list = list()
            if a_news['author'] in id_tag_map:
                index_list.append(a_news['author'])
            if a_news['category'] in id_tag_map:
                index_list.append(a_news['category'])
            if a_news['stock'] in id_tag_map:
                index_list.append(a_news['stock'])
            index_list += a_news['static_tags']
            # 对每个tag，记录文章
            for index in index_list:
                if index not in index_news_set:
                    index_news_set[index] = set()
                index_news_set[index].add(a_news['_id'])
        for index in index_news_set:
            news_set_add = index_news_set[index]
            # 先搜旧有的，拼接后插入
            condition = {'_id': index}
            old_row = table_index.find_one(condition)
            news_set_odd = set(old_row['articles'])
            update = {'$set': {
                'articles': list(set.union(news_set_add, news_set_odd))
            }}
            table_index.update_one(condition, update)
        db.close()

    # 读取csv常量表，返回[tag->id表,id->tag表]
    @staticmethod
    def get_static_map():
        # 字段id_name常量表
        current_abs_path = os.getcwd()
        tag_id_path = os.path.join(current_abs_path, 'static', 'tag_id', 'tag_id.csv')
        tag_id_map = dict()
        id_tag_map = dict()
        with open(tag_id_path, 'r', encoding='GBK') as f:
            reader = csv.reader(f)
            # [0]为id，[1]为内容
            for row in reader:
                row_id = int(row[0])
                id_tag_map[row_id] = row[1]
                tag_id_map[row[1]] = row_id
        return [tag_id_map, id_tag_map]

    @staticmethod
    def handle_cache(tag_id_map):
        db = pymongo.MongoClient('127.0.0.1', 27017)
        table_news = db.yanfuNewsDB.newsTable
        table_cache = db.yanfuNewsDB.newsCacheTable
        table_index = db.yanfuNewsDB.tagIndexTable

        cache = list(table_cache.find({}))
        print(str(len(cache)) + ' news in cache to handle')
        for a_cache in cache:
            news_id = a_cache['_id']
            news_id = int(news_id)
            a_news = table_news.find_one({'_id': news_id}, field)
            if a_news:
                index_list = list()
                tag_list = a_news['tags']
                static_tag_list = a_news['static_tags']
                author = a_news['author']
                category = a_news['category']
                stock = a_news['stock']

                # 新闻本身的信息更新
                for a_tag in a_news['tags']:
                    if a_tag in tag_id_map:
                        tag_list.remove(a_tag)
                        static_tag_list.append(tag_id_map[a_tag])
                if author in tag_id_map:
                    author = tag_id_map[author]
                    index_list.append(author)
                if category in tag_id_map:
                    category = tag_id_map[category]
                    index_list.append(category)
                if stock in tag_id_map:
                    stock = tag_id_map[stock]
                    index_list.append(stock)

                update = {'$set': {
                    'static_tags': static_tag_list,
                    'tags': tag_list,
                    'author': author,
                    'category': category,
                    'stock': stock,
                }}
                table_news.update_one({'_id': news_id}, update)

                # 接下来更改倒排索引
                index_list += static_tag_list

                for index in index_list:
                    # 先搜旧有的，拼接后插入
                    old_row = table_index.find_one({'_id': index})
                    if old_row:
                        news_list = old_row['articles']
                        news_list.append(news_id)
                        update = {'$set': {'articles': news_list}}
                        table_index.update_one({'_id': index}, update)
            table_cache.delete_one({'_id': news_id})
        db.close()
