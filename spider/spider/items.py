# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    _id=scrapy.Field()
    title=scrapy.Field()
    time=scrapy.Field()
    author=scrapy.Field()
    content=scrapy.Field()

    category=scrapy.Field()

    url=scrapy.Field()
    abstract=scrapy.Field()
    score=scrapy.Field()
    tags=scrapy.Field()
    static_tags=scrapy.Field()

    title_hash=scrapy.Field()
    content_hash=scrapy.Field()

    pass
