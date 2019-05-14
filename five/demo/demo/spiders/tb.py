# -*- coding: utf-8 -*-
import scrapy
from lxml import etree
from selenium import webdriver
import time
import random
import requests
from ..items import TBProduct

class TbSpider(scrapy.Spider):
    name = 'tb'
    number = 0
    allowed_domains = ['www.taobao.com']
    start_urls = ['https://item.taobao.com/item.htm?id=576771763547&scm=1007.12144.95220.42296_0_0&pvid=92676c16-1aff-426f-ab1e-2dd0c51449c3&utparam=%7B%22x_hestia_source%22:%2242296%22,%22x_object_type%22:%22item%22,%22x_mt%22:0,%22x_src%22:%2242296%22,%22x_pos%22:3,%22x_pvid%22:%2292676c16-1aff-426f-ab1e-2dd0c51449c3%22,%22x_object_id%22:576771763547%7D']
    request_headers = {
        "connection": "keep-alive",
        "cache-control": "no-cache",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    request_cookies = {
        "thw": "cn", 
        "cna": "HzBgFZ+MAE0CARsm8Sl2SWtw",
        "v": "0",
        "t": "c0c88d51bf9b879f5a0d14daec2ce944",
        "cookie2": "13094148b158e10972b2684924976f4b",
        "_tb_token_": "5b3e38545b9e5", 
        "hng": "CN%7Czh-CN%7CCNY%7C156",
        "skt": "1c716fdfb556d2e1",
        "publishItemObj": "Ng%3D%3D",
        "csg": "a01f54d7",
        "uc3": "vt3=F8dBy3qIgWDx%2B5QUArk%3D&id2=VWn19n9E1CCm&nk2=De6hgvXVESNX&lg2=UIHiLt3xD8xYTw%3D%3D",
        "existShop": "MTU1Nzc0ODExMg%3D%3D",
        "tracknick": "nihao9743",
        "lgc": "nihao9743",
        "_cc_": "V32FPkk%2Fhw%3D%3D", 
        "dnk": "nihao9743",
        "tg": "0",
        "enc": "8qZzWp0kh9KEYZ1uKgzjPVkB%2Ba%2F9n%2F74Pr%2BZtGj8mnCzDTG6ysSfuq0uMbJXY6qE%2FNYi8kPeUEVOAwn8GN1CBA%3D%3D"
    }
    
    TBItem = TBProduct()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers = self.request_headers, cookies = self.request_cookies)

    def parse(self, response):
        if 3 == self.number:
            return
        self.number += 1
        contents = response.body.decode("utf8")
        html = etree.HTML(contents)
        if html.xpath(u"//h3[@class = 'tb-main-title']") and html.xpath(u"//em[@class = 'tb-rmb-num']"):
            title = html.xpath(u"//h3[@class = 'tb-main-title']")[0]
            price = html.xpath(u"//em[@class = 'tb-rmb-num']")[0]
            self.TBItem["title"] = title.text.strip()
            self.TBItem["price"] = price.text
            yield self.TBItem

        hrefs = html.xpath(u"//a")
        for href in hrefs:
            try:
                val = href.attrib["href"]
                if val.startswith("//item.taobao.com"):
                    val = "https:" + val
                    yield scrapy.Request(url = val, callback = self.parse, headers = self.request_headers, cookies = self.request_cookies, dont_filter=True)
            except Exception:
                continue