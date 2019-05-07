# -*- coding: utf-8 -*-
import scrapy
from lxml import etree

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

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers = self.request_headers)

    def parse(self, response):
        print("hello")
        # print(dir(response))
        # print(type(response.body))
        html = response.body.decode("utf8")
        html_page = etree.HTML(html)
        contents = html_page.xpath(u"//a[@href = 'https://news.sina.com.cn/gov/xlxw/2019-05-07/doc-ihvhiqax7082692.shtml']")
        # print(dir(content))
        with open("index.html", "w") as fo:
            for con in contents:
                if con.text:
                    fo.write(str(con.text) + "\n")