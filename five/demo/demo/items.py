# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DemoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class XLProduct(scrapy.Item):
    title = scrapy.Field()
    tarUrl = scrapy.Field()
    md5Url = scrapy.Field()
    last_updated = scrapy.Field(serializer=str)

class TBProduct(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    last_updated = scrapy.Field(serializer=str)

class AmaProduct(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    tarUrl = scrapy.Field()
    md5Url = scrapy.Field()
    last_updated = scrapy.Field(serializer=str)