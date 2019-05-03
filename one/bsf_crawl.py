"""
广度优先算法爬虫
"""
from urllib import request as urllibRequest
from urllib import error as urllibError
from collections import deque
import json
from lxml import etree
import httplib2
import hashlib
from pybloom import BloomFilter
import os
import requests
from logConfig import logger

ignore_file = [".jpg", ".gif"]

class CrawlBSF:
    request_headers = {
        "host": "i.jandan.net",
        "connection": "keep-alive",
        "cache-control": "no-cache",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

    cur_level = 0
    max_level = 5
    dir_name = "iterate/"
    iter_width = 50
    downloaded_urls = []

    du_md5_file_name = dir_name + "download.txt"
    du_url_file_name = dir_name + "urls.txt"

    download_bf = BloomFilter(1024 * 1024 * 16, 0.01)

    cur_queue = deque()
    child_queue = deque()

    def __init__(self, url):
        self.root_url = url
        self.cur_queue.append(url)

        # 创建文件夹和文件
        if not os.path.exists(self.dir_name):
            os.mkdir(self.dir_name)
            with open(self.du_url_file_name, "w"):
                pass
            with open(self.du_md5_file_name, "w"):
                pass

        self.du_file = open(self.du_url_file_name, "a+")

        try:
            self.dumd5_file = open(self.du_md5_file_name, "r")
            self.downloaded_urls = self.dumd5_file.readlines()
            self.dumd5_file.close()
        except Exception as identifier:
            logger.error("%s - File not found -- %s" % (self.du_md5_file_name, identifier))
        finally:
            self.dumd5_file = open(self.du_md5_file_name, "a+")

    def enqueueUrl(self, url):
        self.child_queue.append(url)

    def dequeueUrl(self):
        try:
            url = self.cur_queue.popleft()
            return url
        except Exception as identifier:
            logger.error(identifier)
            self.cur_level += 1
            logger.error("cur_level: " + str(self.cur_level))
            if self.cur_level == self.max_level:
                return
            if 0 == len(self.child_queue):
                return
            self.cur_queue = self.child_queue
            self.child_queue = deque()
            return self.dequeueUrl()

    def getPageContent(self, cur_url):
        logger.error("downloading %s at level %d" % (cur_url, self.cur_level))
        try:
            req = requests.get(cur_url, headers = self.request_headers)
            logger.error("get it %s and status = %s" % (cur_url, req))
            html_page = req.content.decode("utf8")
            filename = cur_url[7:].replace("/", "_")
            with open("%s%s" % (self.dir_name, filename), "w") as fo:
                fo.write(html_page)
        except Exception as identifier:
            logger.error("Error Error: %s" % identifier)
            return
        dumd5 = hashlib.md5(cur_url.encode()).hexdigest()
        self.downloaded_urls.append(dumd5)
        self.dumd5_file.write(dumd5 + "\r\n")
        self.du_file.write(cur_url + "\r\n")
        self.download_bf.add(dumd5)

        html = etree.HTML(html_page.lower())
        if html is None:
            logger.error("None Page")
            return
        hrefs = html.xpath(u"//a")

        for href in hrefs:
            try:
                if "href" in href.attrib:
                    val = href.attrib["href"]
                    logger.info(val)
                    if -1 != val.find("javascript:"):
                        continue
                    if val[-4:] in ignore_file:
                        continue
                    if not val.startswith("http://"):
                        if val.startswith("/"):
                            val = "http://jandan.net" + val
                        else:
                            continue
                    if "/" == val[-1]:
                        val = val[0:-1]
                    # 如果不在布隆过滤里面, 就入队, 否则跳过该url
                    if hashlib.md5(val.encode()).hexdigest() not in self.download_bf:
                        self.enqueueUrl(val)
                    else:
                        logger.error("Skip %s" % val)
            except ValueError as identifier:
                logger.error(identifier)
                continue

    def start(self):
        while True:
            url = self.dequeueUrl()
            if not url:
                break
            self.getPageContent(url)
        self.dumd5_file.close()
        self.du_file.close()

crawler = CrawlBSF("http://jandan.net/")
crawler.start()