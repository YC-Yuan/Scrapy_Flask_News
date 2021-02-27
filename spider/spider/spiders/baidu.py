import logging
import scrapy
import datetime
import os
import re
from spider.items import SpiderItem


class BaiduSpider(scrapy.Spider):
    name = 'baidu'
    allowed_domains = ['baidu.com']
    start_urls = ['https://news.baidu.com/finance']

    def parse(self, response):
        logging.warning('尝试从:' + 'https://news.baidu.com/finance'+'爬取')
        for ul in response.xpath('//ul[@class="ulist fb-list"]'):
            for href in ul.xpath('li/a/@href').extract():
                if re.match(r'^https?:/{2}\w.+$', href):
                    #  print(href)
                    yield scrapy.Request(href, callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        # 形如 发布时间：01-29(或发布时间：2020-01-29)
        date = response.xpath('//span[@class="date"]/text()').extract()
        if not date:
            return

        item = SpiderItem()

        # 形如 09:03
        clock = response.xpath('//span[@class="time"]/text()').extract()

        # 时间戳处理
        # 发布时间：xx-xx
        if date[0][7] == '-':
            month = int(date[0][5:7])
            day = int(date[0][8:10])
            hour = int(clock[0][0:2])
            minute = int(clock[0][3:5])
            timestamp = datetime.datetime(
                datetime.datetime.now().year, month, day, hour, minute, 0, 0)
        # 发布时间：xxxx-xx-xx
        else:
            year = int(date[0][5:9])
            month = int(date[0][10:12])
            day = int(date[0][13:15])
            hour = int(clock[0][0:2])
            minute = int(clock[0][3:5])
            timestamp = datetime.datetime(year, month, day, hour, minute, 0, 0)

        content = response.xpath(
            '//div[@class="article-content"]/p')
        sent_list = list()
        for sent in content:
            sent_list.append(sent.xpath('string(.)').extract()[0])
        content = sent_list

        if len(content) < 4:
            return

        item['title'] = response.xpath(
            '//div[@class="article-title"]/h2/text()').extract()[0]
        item['author'] = response.xpath(
            '//div[@class="author-name"]/a/text()').extract()[0]
        item['time'] = timestamp

        item['content'] = content
        item['abstract'] = item['content'][0]
        if len(item['content']) < 60:
            item['abstract'] += item['content'][1]
        if len(item['content']) < 60:
            item['abstract'] += item['content'][2]
        if len(item['content']) < 60:
            item['abstract'] += item['content'][3]

        item['category'] = '财经'  # 设置为财经

        item['url'] = response.url

        yield item