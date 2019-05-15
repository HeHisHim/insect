# -*- coding: utf-8 -*-
import scrapy
from ..items import AmaProduct
import hashlib
from lxml import etree

# title = scrapy.Field()
# price = scrapy.Field()
# tarUrl = scrapy.Field()
# md5Url = scrapy.Field()

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domains = ['www.amazon.cn']
    start_urls = ['https://www.amazon.cn/dp/B01NAS120J/ref=pd_sbs_14_7?_encoding=UTF8&pd_rd_i=B01NAS120J&pd_rd_r=9c62ea3a-75fb-11e9-948b-bd62f5787111&pd_rd_w=RsuZn&pd_rd_wg=Qd5wO&pf_rd_p=5d917973-0ef4-4b3e-aa18-2becf295a480&pf_rd_r=TDQ2DVR91WFRVTN99M23&psc=1&refRID=TDQ2DVR91WFRVTN99M23', "https://www.amazon.cn/dp/B01NAS120J/ref=pd_sbs_14_7?_encoding=UTF8&pd_rd_i=B01NAS120J&pd_rd_r=9c62ea3a-75fb-11e9-948b-bd62f5787111&pd_rd_w=RsuZn&pd_rd_wg=Qd5wO&pf_rd_p=5d917973-0ef4-4b3e-aa18-2becf295a480&pf_rd_r=TDQ2DVR91WFRVTN99M23&psc=1&refRID=TDQ2DVR91WFRVTN99M23"]
    amaItem = AmaProduct()
    number = 0

    request_headers = {
        "connection": "keep-alive",
        "cache-control": "no-cache",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

    request_cookies = {
        "x-wl-uid": "16P9GJHbt2jYcP4GaNQp2lY6Lb63dF2NM+b6dRBdYQ/oP6/krGhVF3brufmPYEyxfzrB2AG0lor8=", 
        "session-id": "459-1540640-2766058", 
        "ubid-acbcn": "457-9810536-7032715", 
        "session-token": "Y/UfKlCkctigXWa78eaSrKoj6k7izvLfGPCGSRuOwe+2ge3/3Bm/PXO5jbtawAsOx/wXYKmrpTCc8v0ja8dFDpA2pwOymJoGoinZJp7AypcwWcIxaenB+4WiBs+AIrcKSuJ5AijmcWSscpwbCgUXA18L5pgGd4/7AHnU4vZISynm9jOJlgwgYJ0/uD8NK2ncPzksCCyw/6vRuSAf1HHr/dDbTcACesDsRjvd+/arZglWQC9GWKjIKQ==", 
        "i18n-prefs": "CNY", 
        "p2dPopoverID_default_0": "1557802345.608", 
        "p2dPopoverID_all_0": "1557802345.609", 
        "csm-hit=tb" : "s-EW9R6XEAE0692A4V5CGV|1557806287653&t:1557806288889&adb:adblk_no", 
        "session-id-time": "2082729601l"
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url = url, callback = self.parse, headers = self.request_headers, cookies = self.request_cookies, dont_filter = True)

    def parse(self, response):
        # if 10 == self.number:
        #     return
        # self.number += 1
        
        contents = response.body.decode("utf8")

        html = etree.HTML(contents)
        self.amaItem["tarUrl"] = response.url
        self.amaItem["md5Url"] = hashlib.md5(response.url.encode()).hexdigest()

        if html.xpath(u"//span[@id = 'productTitle']") and html.xpath(u"//span[@class = 'a-size-medium a-color-price inlineBlock-display offer-price a-text-normal price3P']"):
            self.amaItem["title"] = html.xpath(u"//span[@id = 'productTitle']")[0].text
            self.amaItem["price"] = html.xpath(u"//span[@class = 'a-size-medium a-color-price inlineBlock-display offer-price a-text-normal price3P']")[0].text.replace("￥", "")
            yield self.amaItem
        
        hrefs = html.xpath(u"//a[@class = 'a-link-normal']")
        for href in hrefs:
            try:
                val = href.attrib["href"]
                if val.startswith("/dp"):
                    val = "https://www.amazon.cn" + val
                    yield scrapy.Request(url = val, callback = self.parse, headers = self.request_headers, dont_filter=True, cookies = self.request_cookies)
            except Exception:
                continue

        



