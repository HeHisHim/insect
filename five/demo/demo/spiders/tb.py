# -*- coding: utf-8 -*-
import scrapy


class TbSpider(scrapy.Spider):
    name = 'tb'
    allowed_domains = ['www.taobao.com']
    start_urls = ['http://www.taobao.com/']

    def parse(self, response):
        pass