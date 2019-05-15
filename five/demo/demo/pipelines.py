# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

class DemoPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline:

    collection_name = "scrapy_items"

    def __init__(self, mongo_uri, mongo_db):
        print("__init__: ", mongo_uri, mongo_db) # __init__:  mongodb://127.0.0.1 robot
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    # from_crawler在 __init__ 调用前 在settings文件获取数据库配置信息
    @classmethod
    def from_crawler(cls, crawler):
        print("from_crawler: ", cls, crawler) # from_crawler:  <class 'demo.pipelines.MongoPipeline'> <scrapy.crawler.Crawler object at 0x10b628a90>
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "items")
        )

    def open_spider(self, spider):
        print("open_spider: ", spider) # open_spider:  <XlSpider 'xl' at 0x10c57d208>
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        print("close_spider:", spider) # close_spider: <XlSpider 'xl' at 0x10c57d208>
        self.client.close()

    def process_item(self, item, spider):
        print("process_item: ", item, spider)
        filterItem = dict(item)
        if self.db[self.collection_name].find({"md5Url": filterItem.get("md5Url")}).count() > 0:
            return
        self.db[self.collection_name].insert_one(filterItem)
        return item