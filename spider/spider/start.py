import sys
import time
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.spiderloader import SpiderLoader

sys.path.append("..")


# 根据项目配置获取 CrawlerProcess 实例
process = CrawlerProcess(get_project_settings())
spider_loader = SpiderLoader(get_project_settings())

# 添加需要执行的爬虫
for spidername in spider_loader.list():
    process.crawl(spidername)

# 执行
process.start()
