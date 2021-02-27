
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
import urllib
import pymongo
import jieba.analyse
from datetime import datetime
from spider.utils.snowflake import snowflake_00
from itemadapter import ItemAdapter
from spider.utils import para_analyse
from spider.utils.int64hash import Int64Hash


class SpiderPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client['yanfuNewsDB']
        self.table = self.db['newsTable']
        self.table_cache = self.db['newsCacheTable']
        self.snowflake = snowflake_00  # 数据表编号

    def process_item(self, item, spider):
        # 处理标题和内容 生成hash值
        title = item['title']
        content = item['content']
        content = ''.join(content)
        content_list = para_analyse.cut_sent(content)
        sent = para_analyse.longest_sent(content_list)
        content_hash = Int64Hash.as_int(sent)
        title_hash = Int64Hash.as_int(title)

        check_title = self.table.find_one({'title_hash': title_hash})
        check_url = self.table.find_one({'url': item['url']})
        check_content = self.table.find_one({'content_hash': content_hash})
        check = check_title or check_content or check_url
        # 不重复，收录新文章
        if not check:
            id = self.snowflake.get_id()
            item['_id'] = int(id)

            item['score'] = grade_item(item)

            # 关键词提取
            sentence = ''.join(item['content'])
            keys_TFIDF = jieba.analyse.extract_tags(
                sentence, topK=10, allowPOS=(['ns', 'n', 'vn']))
            keys_textrank = jieba.analyse.textrank(
                sentence, topK=10, withWeight=False, allowPOS=('ns', 'n', 'vn'))
            keys = [x for x in keys_TFIDF if x in keys_textrank]
            item['tags'] = keys

            item['title_hash'] = title_hash
            item['content_hash'] = content_hash
            item['static_tags'] = list()

            length = 0
            for sentence in item['content']:
                length += len(sentence)

            # 载入数据库
            postItem = dict(item)
            self.table.insert(postItem)

            logging.warning('爬取新页面:'+item['url'] +
                            ',存储了'+str(len(keys))+'个tag,'+str(length)+'字,数据库id为'+str(item['_id']))

            # 将新增的文章放入数据库缓存表，服务器需要持续处理文章增量
            self.table_cache.insert_one({'_id': item['_id']})

            return item
        else:
            if check_content and not check_url:
                pass
                # logging.warning('在未存储的url分析出已存储的文章内容，已存储页面：'+str(check_content['url'])+'，判断重复的页面：'+str(item['url']))


def grade_item(item):
    # delta = datetime.now()-item['time']
    # score = 100-delta.days
    # return score
    return 100
