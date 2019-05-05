"""
多线程爬虫
"""
import sys
sys.path.append("..")
import time

from collections import deque
import json
from lxml import etree
import httplib2
import hashlib
from pybloom import BloomFilter
import os
import requests
import threading
from logConfig import logger

ignore_file = [".jpg", ".gif"]
CRAWL_DELAY = 0.6

class CrawlBSF:
    request_headers = {
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
    num_downloaded_pages = 0
    downloaded_urls = []

    du_md5_file_name = dir_name + "download.txt"
    du_url_file_name = dir_name + "urls.txt"

    bloom_downloaded_urls = BloomFilter(1024 * 1024 * 16, 0.01)
    bloom_url_queue = BloomFilter(1024 * 1024 * 16, 0.01)

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
        
        try:
            with open(self.du_md5_file_name, "r") as fo:
                self.downloaded_urls = fo.readlines()
            for urlmd5 in self.downloaded_urls:
                self.bloom_downloaded_urls.add(urlmd5[:-2])
        except Exception as identifier:
            logger.error(identifier)

    def enqueueUrl(self, url):
        urlmd5 = hashlib.md5(url.encode()).hexdigest()
        if url not in self.bloom_url_queue and urlmd5 not in self.bloom_downloaded_urls:
            self.child_queue.append(url)
            self.bloom_url_queue.add(url)
        else:
            logger.info("Skip %s" % url)

    def dequeUrl(self):
        try:
            url = self.cur_queue.popleft()
            return url
        except Exception as identifier:
            logger.error(identifier)
            return None

    def getPageContent(self, cur_url):
        logger.info("downloading %s at level %d" % (cur_url, self.cur_level))
        try:
            req = requests.get(cur_url)
            html_page = req.content.decode("utf8")
            if cur_url.startswith("https"):
                filename = cur_url[8:].replace("/", "_")
            else:
                filename = cur_url[7:].replace("/", "_")
            if filename.endswith(".html"):
                with open("%s%s" % (self.dir_name, filename), "w") as fo:
                    fo.write(html_page)
            else:
                with open("%s%s.html" % (self.dir_name, filename), "w") as fo:
                    fo.write(html_page)
        except Exception as identifier:
            logger.error(identifier)
            return None

        dumd5 = hashlib.md5(cur_url.encode()).hexdigest()
        self.downloaded_urls.append(dumd5)
        with open(self.du_md5_file_name, "a") as fo:
            fo.write(dumd5 + "\r\n")
        with open(self.du_url_file_name, "a") as fo:
            fo.write(cur_url + "\r\n")
        
        self.bloom_downloaded_urls.add(dumd5)

        self.num_downloaded_pages += 1

        html = etree.HTML(html_page.lower())
        if html is None:
            logger.error("None Page")
            return
        hrefs = html.xpath(u"//a")

        for href in hrefs:
            try:
                if "href" in href.attrib:
                    val = href.attrib["href"]
                    if -1 != val.find("javascript:"):
                        continue
                    elif val[-4:] in ignore_file:
                        continue
                    elif not (val.startswith("http://") or val.startswith("https://")):
                        if val.startswith("/"):
                            val = "https://www.sina.com.cn/" + val
                        else:
                            continue
                    elif "/" == val[-1]:
                        val = val[0:-1]
                    self.enqueueUrl(val)
            except Exception as identifier:
                logger.error(identifier)
                continue

def main():
    crawl = CrawlBSF("https://www.sina.com.cn/")
    start_time = time.time()

    # 控制如果是第一个页面就阻塞去抓, 后续页面看多线程去抓
    is_root_page = True

    threads = []
    max_threads = 10

    while True:
        url = crawl.dequeUrl()

        if not url:
            # 进入下一层级前等待上一层爬取的线程join
            crawl.cur_level += 1
            logger.info("cur_level: %d", crawl.cur_level)
            for th in threads:
                th.join()
            if crawl.cur_level == crawl.max_level:
                break
            if 0 == len(crawl.child_queue):
                break
            crawl.cur_queue = crawl.child_queue
            crawl.child_queue = deque()
            continue
        
        if is_root_page:
            crawl.getPageContent(url)
            is_root_page = False
        else:
            while True:
                # 将完成任务的线程移除
                for th in threads[:]:
                    if not th.is_alive():
                        threads.remove(th)
                if max_threads <= len(threads):
                    time.sleep(CRAWL_DELAY)
                    continue
                
                try:
                    th = threading.Thread(target = crawl.getPageContent, args = (url, ))
                    threads.append(th)
                    th.setDaemon(True)
                    th.start()
                    time.sleep(CRAWL_DELAY)
                    break
                except Exception as identifier:
                    logger.error(identifier)
    
    logger.info("%d pages downloads, time cost %0.2f seconds " % (crawl.num_downloaded_pages, time.time() - start_time))

if __name__ == "__main__":
    main()