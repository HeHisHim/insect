# -*- coding: utf-8 -*-
import scrapy
from lxml import etree
from selenium import webdriver
import time
import random
import requests

class VerifycodeSpider(scrapy.Spider):
    name = 'verifyCode'
    allowed_domains = ['www.me.html']
    start_urls = ['http://127.0.0.1/register.html']

    def parse(self, response):
        contents = response.body
        html = etree.HTML(contents)
        target = html.xpath(u"//div[@class = 'input-group-addon image-code']/img")
        binImage = "http://127.0.0.1" + target[0].attrib["src"]
        res = requests.get(binImage)
        img = res.content
        with open("index%s.png" % random.randint(0, 10000), "wb") as fo:
            fo.write(img)
        
