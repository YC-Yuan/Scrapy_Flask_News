import logging
import scrapy
import datetime
import os
import re
import time
from spider.items import SpiderItem


class SinaSpider(scrapy.Spider):
    name = 'sina'
    allowed_domains = ['sina.com.cn']
    start_urls = ['https://finance.sina.com.cn/']

    def parse(self, response):
        logging.warning('尝试从:' + 'https://finance.sina.com.cn/'+'爬取')
        href_list = list()
        for href in response.xpath('//a[string-length(text())>10]/@href').extract():
            # print(href)
            if re.match(r'^https?:/{2}\w.+$', href):
                href_list.append(href)
        for href in href_list:
            yield scrapy.Request(href, callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        date = response.xpath('//span[@class="date"]/text()').extract()
        if not date:
            return

        item = SpiderItem()

        date = date[0]
        if len(date) == 17:
            year = int(date[0:4])
            month = int(date[5:7])
            day = int(date[8:10])
            hour = int(date[12:14])
            minute = int(date[15:])
            timestamp = datetime.datetime(year, month, day, hour, minute, 0, 0)
        elif len(date) == 19:
            year = int(date[0:4])
            month = int(date[5:7])
            day = int(date[8:10])
            hour = int(date[11:13])
            minute = int(date[14:16])
            second = int(date[17:])
            timestamp = datetime.datetime(
                year, month, day, hour, minute, second, 0)
        else:
            return
        content = response.xpath('//div[@class="article"]/p')
        sent_list = list()
        for sent in content:
            sent_list.append(sent.xpath('string(.)').extract()[0])
        content = sent_list  # 此时的content为原始文章内容，许多段落开头空了两格

        sent_list = list()
        for a_sent in content:
            sent_list.append(a_sent.strip('\u3000'))
        content = sent_list  # 去除了空两格问题

        if len(content) < 4:
            return
        item['title'] = response.xpath(
            '//h1[@class="main-title"]/text()').extract()[0]
        author = response.xpath(
            '//a[contains(@class,"source")]/text()').extract()
        if author:
            author = author[0]
        else:
            author = response.xpath(
                '//span[contains(@class,"source")]/text()').extract()[0]
        item['author'] = author
        item['time'] = timestamp
        item['content'] = content
        item['abstract'] = item['content'][0]
        if len(item['content']) < 60:
            item['abstract'] += item['content'][1]
        if len(item['content']) < 60:
            item['abstract'] += item['content'][2]
        if len(item['content']) < 60:
            item['abstract'] += item['content'][3]

        category = response.xpath(
            '//div[@class="channel-path"]/a/text()').extract()
        if category:
            category = category[0].strip()
        else:
            category = response.xpath(
                '//div[@class="channel-path"]/text()').extract()
            if category:
                category = category[0].strip()
                if not category:
                    category = '财经'  # 设置为财经
            else:
                category = '财经'  # 设置为财经
        item['category'] = category
        item['url'] = response.url
        yield item
