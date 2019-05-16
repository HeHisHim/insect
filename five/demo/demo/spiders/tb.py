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
    start_urls = ['https://item.taobao.com/item.htm?spm=a230r.1.14.20.6e5f411er7xBrP&id=576637081854&ns=1&abbucket=12#detail']
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
        contents = response.body.decode("utf8")
        with open("index.html", "w") as fo:
            fo.write(contents)