# -*- coding: utf-8 -*-
import scrapy
from lxml import etree
from ..items import XLProduct
import hashlib

class XlSpider(scrapy.Spider):
    request_headers = {
        "connection": "keep-alive",
        "cache-control": "no-cache",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    name = 'xl'
    allowed_domains = ['news.sina.com.cn']
    start_urls = ['http://news.sina.com.cn/']
    # 用 XLItem 来装爬取的信息
    XLItem = XLProduct()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers = self.request_headers)

    def parse(self, response):
        html = response.body.decode("utf8")
        html_page = etree.HTML(html)
        contents = html_page.xpath(u"//div[@id='ad_entry_b2']//ul//li//a")
        # with open("index.html", "w") as fo:
        #     for con in contents:
        #         if con.text:
        #             fo.write(str(con.text) + str(con.attrib["href"]) + "\n")
        for con in contents:
            if con.text:
                self.XLItem["title"] = con.text
                self.XLItem["tarUrl"] = con.attrib["href"]
                self.XLItem["md5Url"] = hashlib.md5(self.XLItem["tarUrl"].encode()).hexdigest()
                """
                parse方法 要么yield一个字典类型 要么yield一个scrapy.Request
                当为字典类型: 数据会通过pipelines.py的类处理
                当为scrapy.Request, 数据会继续调用parse
                """
                yield self.XLItem